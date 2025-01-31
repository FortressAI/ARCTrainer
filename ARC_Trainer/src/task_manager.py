import os
import json
import random
import uuid
from pathlib import Path

from flask import current_app, send_file, jsonify
from loguru import logger
from neo4j import GraphDatabase
from PIL import Image, ImageDraw
import requests

from src.llm_client import LLMClient
from src.PrologRuleGenerator import PrologRuleGenerator
from src.learning_agent import LearningAgent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = Path(BASE_DIR) / "datasets/evaluation"
IMAGE_DIR = Path(BASE_DIR) / "generated_images"
IMAGE_DIR.mkdir(exist_ok=True)

HF_BLIP_ENDPOINT = os.getenv("HF_BLIP_ENDPOINT", "")
HF_BEARER_TOKEN = os.getenv("HF_BEARER_TOKEN", "")

class TaskManager:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="mysecurepassword"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.llm_client = LLMClient()
        self.prolog_generator = PrologRuleGenerator()
        self.learning_agent = LearningAgent()
        logger.info("✅ TaskManager initialized with structured ARC support.")

    def close(self):
        self.driver.close()

    def get_random_task(self):
        """
        Picks a random ARC puzzle from dataset directory, then does the pipeline:
         1. Check or create puzzle in KG
         2. Generate images for train/test input
         3. Optionally call BLIP on them
         4. Call LLM for a text-based answer (not JSON)
         5. Store everything
         6. Return puzzle data + raw LLM text
        """
        files = [f.stem for f in DATASET_DIR.glob("*.json")]
        if not files:
            return {"error": "No available ARC tasks."}, 404

        puzzle_name = random.choice(files)
        return self._process_full_puzzle_flow(puzzle_name)

    def load_arc_task(self, task_name="default_task", reveal_solution=False):
        """
        Older approach: loads puzzle data from JSON, optionally revealing solution. 
        """
        task_path = DATASET_DIR / f"{task_name}.json"
        logger.info(f"🔍 Checking ARC task file path: {task_path}")

        if not task_path.exists():
            logger.error(f"❌ Task file does not exist: {task_path}")
            return {"error": f"Task '{task_name}' not found in dataset"}, 404

        try:
            with open(task_path, "r") as file:
                task_data = json.load(file)
                if not self.validate_task_data(task_data):
                    raise ValueError("Invalid task format.")
                logger.info(f"✅ Successfully loaded task: {task_name}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"❌ JSON error in {task_name}.json: {str(e)}")
            return {"error": f"Invalid JSON format in task '{task_name}'"}, 500

        # Minimal approach: store puzzle, generate images
        self.init_puzzle_in_kg(task_name, task_data)
        self.process_puzzle_grids(task_name, task_data, skip_test_output_blip=False)

        correct_solutions = []
        if reveal_solution:
            for t_ex in task_data.get("test", []):
                correct_solutions.append(t_ex.get("output", []))

        response = {
            "name": task_name,
            "train": task_data.get("train", []),
            "test": task_data.get("test", []),
            "correct_solutions": correct_solutions
        }
        return response, 200

    def _process_full_puzzle_flow(self, puzzle_name):
        """
        The new pipeline, but LLM output is raw text only (no JSON parse).
        """
        task_path = DATASET_DIR / f"{puzzle_name}.json"
        if not task_path.exists():
            return {"error": f"Task '{puzzle_name}' not found in dataset"}, 404

        try:
            with open(task_path, "r") as file:
                puzzle_data = json.load(file)
                if not self.validate_task_data(puzzle_data):
                    raise ValueError("Invalid puzzle format.")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON error in {puzzle_name}.json: {e}")
            return {"error": f"Invalid JSON format in '{puzzle_name}'"}, 500

        logger.info(f"✅ Loaded puzzle data for {puzzle_name}")

        # 1. Initialize puzzle in KG if not present
        self.init_puzzle_in_kg(puzzle_name, puzzle_data)

        # 2. Generate images & call BLIP for training + test input, skipping test output
        train_descriptions = []
        test_input_descriptions = []

        # Process training pairs
        for i, example in enumerate(puzzle_data.get("train", [])):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])

            in_filename = self.generate_png(puzzle_name, in_grid, f"train_input_{i}")
            out_filename = self.generate_png(puzzle_name, out_grid, f"train_output_{i}")

            desc_in = self._maybe_call_blip(in_filename)
            desc_out = self._maybe_call_blip(out_filename)

            train_descriptions.append({
                "index": i,
                "input_desc": desc_in,
                "output_desc": desc_out
            })

        # Process test pairs
        for j, example in enumerate(puzzle_data.get("test", [])):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])

            in_filename = self.generate_png(puzzle_name, in_grid, f"test_input_{j}")
            desc_in = self._maybe_call_blip(in_filename)

            out_filename = self.generate_png(puzzle_name, out_grid, f"test_output_{j}")
            desc_out = None  # skipping BLIP for test output

            test_input_descriptions.append({
                "index": j,
                "input_desc": desc_in,
                "real_output_grid": out_grid
            })

        # 3. Build prompt, call LLM -> Raw text
        llm_prompt = self.build_llm_prompt(puzzle_name, train_descriptions, test_input_descriptions)
        llm_response = self.llm_client.query_llm(llm_prompt)
        raw_llm_text = llm_response.get("response", "")

        # 4. We do NOT parse it as JSON. So no compare. success = False
        success = False

        # 5. Store the raw text in KG
        self.log_llm_solution(
            puzzle_name,
            llm_text=raw_llm_text,
            success=success
        )

        # 6. Return puzzle data (train/test) plus raw LLM text
        result = {
            "task_name": puzzle_name,
            "train": puzzle_data["train"],  
            "test": puzzle_data["test"],
            "llm_text": raw_llm_text,
            "success": success
        }
        return result, 200

    def validate_task_data(self, task_data):
        return isinstance(task_data, dict) and "train" in task_data and "test" in task_data

    def init_puzzle_in_kg(self, task_name, puzzle_data):
        with self.driver.session() as session:
            record = session.run(
                "MATCH (t:Task {name: $name}) RETURN t LIMIT 1",
                name=task_name
            ).single()
            if record is None:
                session.run(
                    """
                    CREATE (t:Task {name: $name, domain: 'arc'})
                    """,
                    name=task_name
                )
                logger.info(f"✅ Created puzzle '{task_name}' in KG.")

    def process_puzzle_grids(self, task_name, task_data, skip_test_output_blip=False):
        """
        Old helper used by load_arc_task. 
        We'll keep it but no changes to the code.
        """
        idx = 0
        for example in task_data.get("train", []):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])

            in_filename = self.generate_png(task_name, in_grid, f"train_input_{idx}")
            out_filename = self.generate_png(task_name, out_grid, f"train_output_{idx}")

            if HF_BLIP_ENDPOINT and HF_BEARER_TOKEN:
                desc_in = self.call_blip_on_image(in_filename)
                desc_out = self.call_blip_on_image(out_filename)
                logger.info(f"[BLIP-TRAIN] Input({idx}): {desc_in}")
                logger.info(f"[BLIP-TRAIN] Output({idx}): {desc_out}")
            idx += 1

        idx = 0
        for example in task_data.get("test", []):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])

            in_filename = self.generate_png(task_name, in_grid, f"test_input_{idx}")
            if HF_BLIP_ENDPOINT and HF_BEARER_TOKEN:
                desc_in = self.call_blip_on_image(in_filename)
                logger.info(f"[BLIP-TEST] Input({idx}): {desc_in}")

            out_filename = self.generate_png(task_name, out_grid, f"test_output_{idx}")
            if HF_BLIP_ENDPOINT and HF_BEARER_TOKEN and not skip_test_output_blip:
                desc_out = self.call_blip_on_image(out_filename)
                logger.info(f"[BLIP-TEST] Output({idx}): {desc_out}")
            idx += 1

    def generate_png(self, task_name, grid, label):
        if not grid or not isinstance(grid, list):
            logger.warning("Grid is empty or invalid, skipping PNG generation.")
            return None

        rows = len(grid)
        cols = max(len(r) for r in grid) if rows > 0 else 0
        cell_size = 20
        img_width = cols * cell_size
        img_height = rows * cell_size

        img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(img)

        color_map = {
            0: (0, 0, 0),
            1: (0, 116, 217),
            2: (255, 65, 54),
            3: (46, 204, 64),
            4: (255, 220, 0),
            5: (170, 170, 170),
            6: (240, 18, 190),
            7: (255, 133, 27),
            8: (127, 219, 255),
            9: (135, 12, 37),
        }

        for r in range(rows):
            for c, val in enumerate(grid[r]):
                color = color_map.get(val, (255, 255, 255))  # default white if unknown
                x0 = c * cell_size
                y0 = r * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                draw.rectangle([x0, y0, x1, y1], fill=color)

        filename = f"{task_name}_{label}.png"
        filepath = IMAGE_DIR / filename
        img.save(filepath)
        logger.info(f"Generated PNG: {filepath}")
        return filepath

    def call_blip_on_image(self, image_path):
        if not os.path.exists(image_path):
            return "No image found for BLIP"

        url = HF_BLIP_ENDPOINT
        headers = {"Authorization": f"Bearer {HF_BEARER_TOKEN}"}
        files = {"file": open(image_path, "rb")}
        payload = {"options": {"beam_search": True}}

        try:
            response = requests.post(url, headers=headers, files=files, data=payload)
            response.raise_for_status()
            data = response.json()
            caption = data.get("caption", "No caption from BLIP.")
            return caption
        except Exception as e:
            logger.error(f"BLIP call failed: {e}")
            return "BLIP call failed"

    def _maybe_call_blip(self, file_path):
        if not file_path:
            return "No grid or invalid file path."
        if HF_BLIP_ENDPOINT and HF_BEARER_TOKEN:
            return self.call_blip_on_image(file_path)
        return "BLIP not configured."

    def build_llm_prompt(self, task_name, train_descs, test_descs):
        train_str = ""
        for td in train_descs:
            train_str += f"\nTrain Example {td['index']}:\n" \
                         f"Input Description: {td['input_desc']}\n" \
                         f"Output Description: {td['output_desc']}\n"

        test_str = ""
        for ttd in test_descs:
            test_str += f"\nTest Example {ttd['index']}:\n" \
                        f"Input Description: {ttd['input_desc']}\n"

        # We may mention 'generate a solution' in text, 
        # but we won't parse it as JSON. 
        prompt = f"""
You have an ARC puzzle '{task_name}'. 
Below are training examples, each with an input grid described in words plus its output grid.

TRAINING EXAMPLES:
{train_str}

TEST EXAMPLES:
{test_str}

Please provide your thoughts or a potential solution in plain text. We won't parse JSON. 
"""
        return prompt.strip()

    # Removed parse_llm_guess since we no longer parse JSON.

    # Removed compare_grids or keep if you want. We'll show a version that we remove:

    # def compare_grids(...): pass  # not used now, so you can delete it

    def log_llm_solution(self, task_name, llm_text, success):
        """
        Store the raw LLM text in KG. We skip guess_grid.
        """
        with self.driver.session() as session:
            session.run(
                """
                MERGE (t:Task {name: $task_name})
                SET t.llm_text = $llm_text,
                    t.success = $success
                """,
                task_name=task_name,
                llm_text=llm_text,
                success=success
            )
            if not success:
                session.run(
                    """
                    MATCH (t:Task {name: $task_name})
                    MERGE (c:Counterexample {id: $cid})
                    MERGE (t)-[:HAS_COUNTEREXAMPLE]->(c)
                    SET c.llm_text = $llm_text
                    """,
                    task_name=task_name,
                    cid=str(uuid.uuid4()),
                    llm_text=llm_text
                )
            logger.info(f"Logged raw LLM text & success={success} for {task_name} in KG.")

    def attempt_solution(self, loaded_data, user_solution=None):
        """
        Old approach: if you still want it, we keep it. 
        But we won't parse the LLM's guess as JSON either here.
        We'll just store it as text, success = False always.
        """
        task_name = loaded_data.get("name", "unknown_task")
        history = self.check_knowledge_graph(task_name)
        if history and history["success"]:
            logger.info("Returning previously stored solution from KG.")
            return [], True  # No guess grid, just empty

        puzzle_str = json.dumps(loaded_data.get("train", []), indent=2)
        prompt = f"Given this ARC puzzle data:\n{puzzle_str}\nTalk about a potential solution in plain text."
        ai_response = self.llm_client.query_llm(prompt)
        raw_text = ai_response.get("response", "")

        success = False
        self.log_llm_solution(task_name, raw_text, success)
        return [], success

    def check_knowledge_graph(self, task_name):
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (t:Task {name: $task_name})
                RETURN t.llm_text AS llm_text, t.success AS success
                """,
                task_name=task_name
            ).single()
            if record and record["llm_text"] is not None:
                return {
                    "llm_text": record["llm_text"],
                    "success": record["success"]
                }
            return None

    def load_lhe_task(self, task_name="default_lhe"):
        return {"error": "LHE not implemented."}, 200
