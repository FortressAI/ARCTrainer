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

from dotenv import load_dotenv

load_dotenv()
# Load .env file


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
        Picks a random ARC puzzle from the dataset directory, then:
         1. Checks/creates puzzle in KG
         2. Generates images for train/test input
         3. Optionally calls BLIP on them
         4. Calls LLM for a text-based answer (no JSON)
         5. Stores everything
         6. Returns puzzle data + raw LLM text
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

    def extract_grid_details(self, grid, blip_desc):
        """
        Extracts structured details about a grid:
        - Size (rows x cols)
        - Unique colors present
        - BLIP-generated description (if available)
        """
        if not isinstance(grid, list) or not grid:
            return {
                "size": "Unknown",
                "colors": [],
                "details": "No grid data available"
            }

        rows = len(grid)
        cols = max(len(r) for r in grid) if rows > 0 else 0
        unique_colors = sorted({cell for row in grid for cell in row})

        return {
            "size": f"{rows}x{cols}",
            "colors": unique_colors,
            "details": blip_desc if blip_desc else "No BLIP description available"
        }

    def _process_full_puzzle_flow(self, puzzle_name):
        """
        The main pipeline for processing an ARC puzzle.
        - Loads puzzle data
        - Generates grid images
        - Calls BLIP for descriptions
        - Constructs a detailed LLM prompt
        - Queries the LLM for reasoning
        - Stores results in the knowledge graph
        - Returns puzzle data with LLM response
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

        # 1. Initialize puzzle in Knowledge Graph if not already present
        self.init_puzzle_in_kg(puzzle_name, puzzle_data)

        # 2. Generate images & call BLIP to describe training/test examples
        train_descriptions = []
        test_input_descriptions = []

        # Process training examples
        for i, example in enumerate(puzzle_data.get("train", [])):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])

            # Generate images
            in_filename = self.generate_png(puzzle_name, in_grid, f"train_input_{i}")
            out_filename = self.generate_png(puzzle_name, out_grid, f"train_output_{i}")

            # Call BLIP for descriptions
            desc_in = self._maybe_call_blip(in_filename)
            desc_out = self._maybe_call_blip(out_filename)

            # Store structured descriptions
            train_descriptions.append({
                "index": i,
                "input_desc": self.extract_grid_details(in_grid, desc_in),
                "output_desc": self.extract_grid_details(out_grid, desc_out)
            })

        # Process test examples
        for j, example in enumerate(puzzle_data.get("test", [])):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])  # Used for comparison but not for BLIP

            # Generate images
            in_filename = self.generate_png(puzzle_name, in_grid, f"test_input_{j}")

            # Call BLIP for description
            desc_in = self._maybe_call_blip(in_filename)

            # Store structured descriptions
            test_input_descriptions.append({
                "index": j,
                "input_desc": self.extract_grid_details(in_grid, desc_in),
                "real_output_grid": out_grid  # Used for validation later
            })

        # 3. Debugging: Ensure BLIP descriptions are present before calling LLM
        for td in train_descriptions:
            logger.info(f"📖 Train Example {td['index']} - Input: {td['input_desc']}")
            logger.info(f"📖 Train Example {td['index']} - Output: {td['output_desc']}")
        for td in test_input_descriptions:
            logger.info(f"📖 Test Example {td['index']} - Input: {td['input_desc']}")

        # 4. Build improved LLM prompt using structured descriptions
        llm_prompt = self.build_llm_prompt(puzzle_name, train_descriptions, test_input_descriptions)

        # 5. Query LLM for reasoning & predictions
        llm_response = self.llm_client.query_llm(llm_prompt)
        raw_llm_text = llm_response.get("response", "")

        # 6. Compare LLM's response with expected output grid (if available)
        success = False
        if test_input_descriptions:
            real_output = test_input_descriptions[0]["real_output_grid"]
            predicted_output = self.parse_llm_guess(raw_llm_text)  # Convert response to a grid

            if self.compare_grids(predicted_output, real_output):
                success = True

        # 7. Store LLM analysis in knowledge graph
        self.log_llm_solution(
            puzzle_name,
            llm_text=raw_llm_text,
            success=success
        )

        # 8. Return puzzle data + LLM response for UI
        result = {
            "task_name": puzzle_name,
            "train": puzzle_data["train"],  # Essential for UI
            "test": puzzle_data["test"],  # Essential for UI
            "llm_text": raw_llm_text,  # Full reasoning from LLM
            "success": success  # Did LLM get it right?
        }
        return result, 200


    def parse_llm_guess(self, llm_response):
        """
        Parses the LLM response to extract a predicted output grid.
        
        If the response contains structured JSON, it parses it. 
        Otherwise, it extracts the grid information from the text.
        
        Returns:
            - A structured grid if successfully extracted.
            - The raw response if no grid can be parsed.
        """
        if not llm_response or not isinstance(llm_response, str):
            logger.warning("⚠️ LLM response is empty or invalid.")
            return "LLM response was empty or not in expected format."

        # Attempt to extract JSON grid if present
        try:
            guess = json.loads(llm_response)
            if isinstance(guess, list):  # Check if it's a valid grid
                logger.info("✅ Successfully parsed LLM grid output.")
                return guess
        except json.JSONDecodeError:
            logger.warning("⚠️ LLM response was not valid JSON. Attempting text extraction.")

        # Extract grid details using regex
        grid_size_match = re.search(r"Output Grid Size[:\s]+(\d+)x(\d+)", llm_response)
        colors_match = re.search(r"Colors Present[:\s]+\[([0-9,\s]+)\]", llm_response)

        if grid_size_match and colors_match:
            rows, cols = int(grid_size_match.group(1)), int(grid_size_match.group(2))
            colors = list(map(int, colors_match.group(1).split(',')))

            # Construct an empty grid filled with zero (or inferred from colors)
            default_fill = colors[0] if colors else 0
            parsed_grid = [[default_fill for _ in range(cols)] for _ in range(rows)]

            logger.info(f"✅ Extracted grid of size {rows}x{cols} with colors {colors}.")
            return parsed_grid

        logger.warning("⚠️ Could not extract structured grid from LLM response. Returning raw text.")
        return llm_response  # Fallback to returning the full response

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
        Processes ARC puzzle grids by:
        1. Generating PNG images for visualization.
        2. Calling BLIP for descriptions (if available).
        3. Structuring grid data (size, colors) into a human-readable format.
        4. Ensuring descriptions are fully prepared before calling LLM.
        """
        train_descriptions = []
        test_input_descriptions = []

        def extract_grid_info(grid):
            """Extracts size and unique colors from a given grid."""
            rows = len(grid)
            cols = len(grid[0]) if rows > 0 else 0
            unique_colors = sorted(set(cell for row in grid for cell in row))
            return {
                "size": f"{rows}x{cols}",
                "colors": unique_colors
            }

        # Process training examples
        for i, example in enumerate(task_data.get("train", [])):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])

            # Extract grid metadata
            input_info = extract_grid_info(in_grid)
            output_info = extract_grid_info(out_grid)

            # Generate PNG images
            in_filename = self.generate_png(task_name, in_grid, f"train_input_{i}")
            out_filename = self.generate_png(task_name, out_grid, f"train_output_{i}")

            # Call BLIP for descriptions
            desc_in = self._maybe_call_blip(in_filename) if in_filename else "BLIP not available"
            desc_out = self._maybe_call_blip(out_filename) if out_filename else "BLIP not available"

            # Build structured descriptions
            train_descriptions.append({
                "index": i,
                "input_desc": {
                    "size": input_info["size"],
                    "colors": input_info["colors"],
                    "details": desc_in
                },
                "output_desc": {
                    "size": output_info["size"],
                    "colors": output_info["colors"],
                    "details": desc_out
                }
            })

        # Process test examples
        for j, example in enumerate(task_data.get("test", [])):
            in_grid = example.get("input", [])
            out_grid = example.get("output", [])  # Output is unknown during testing

            # Extract grid metadata
            input_info = extract_grid_info(in_grid)

            # Generate PNG for test input
            in_filename = self.generate_png(task_name, in_grid, f"test_input_{j}")

            # Call BLIP for input description (skip test output)
            desc_in = self._maybe_call_blip(in_filename) if in_filename else "BLIP not available"

            # Store structured test input data
            test_input_descriptions.append({
                "index": j,
                "input_desc": {
                    "size": input_info["size"],
                    "colors": input_info["colors"],
                    "details": desc_in
                },
                "real_output_grid": out_grid  # Stored for validation after LLM response
            })

        return train_descriptions, test_input_descriptions

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

    def call_blip_on_image(self, image_path, custom_prompt=None):
        """
        Calls the BLIP model via Hugging Face API to generate a description for the given image.
        Allows sending a custom prompt for better control over the generated text.
        """
        if not HF_BLIP_ENDPOINT or not HF_BEARER_TOKEN:
            logger.warning("BLIP API is not configured properly. Skipping image processing.")
            return "BLIP not configured."

        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return "No image found for BLIP."

        try:
            # Read the image and encode it as base64
            with open(image_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            # Default prompt if none provided
            prompt = custom_prompt or "Describe the pattern in this grid as accurately as possible."

            # Prepare JSON payload with image & instruction
            payload = {
                "inputs": {
                    "image": img_base64,
                    "prompt": prompt  # Sending additional instructions
                },
                "parameters": {"beam_search": True}  # Optional tuning params
            }

            headers = {
                "Authorization": f"Bearer {HF_BEARER_TOKEN}",
                "Content-Type": "application/json"
            }

            # Make POST request to Hugging Face API
            response = requests.post(HF_BLIP_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Parse response
            data = response.json()
            caption = data.get("caption", "No description generated.")

            logger.info(f"BLIP Response: {caption}")
            return caption

        except requests.exceptions.RequestException as e:
            logger.error(f"BLIP API request failed: {e}")
            return "BLIP call failed."
    def _maybe_call_blip(self, file_path):
        """
        Calls BLIP for image captioning if configured.
        Returns either the BLIP-generated description or a default response.
        """
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"⚠️ No valid image file at {file_path}. Skipping BLIP call.")
            return "No image found for description."

        if not HF_BLIP_ENDPOINT or not HF_BEARER_TOKEN:
            logger.warning("⚠️ BLIP is not configured. Skipping description generation.")
            return "BLIP not configured."

        return self.call_blip_on_image(file_path)

    def build_llm_prompt(self, task_name, train_descs, test_descs):
        """
        Creates a structured LLM prompt that describes the puzzle in a way that mimics human reasoning.
        """
        train_str = "Training Examples:\n"
        for td in train_descs:
            train_str += f"Example {td['index']}:\n"
            train_str += f"  - Input Grid Size: {td['input_desc']['size']}\n"
            train_str += f"  - Colors Present: {td['input_desc']['colors']}\n"
            train_str += f"  - BLIP Description: {td['input_desc']['details']}\n"
            train_str += f"  - Output Grid Size: {td['output_desc']['size']}\n"
            train_str += f"  - Colors Present: {td['output_desc']['colors']}\n"
            train_str += f"  - BLIP Description: {td['output_desc']['details']}\n\n"

        test_str = "Test Examples:\n"
        for ttd in test_descs:
            test_str += f"Example {ttd['index']}:\n"
            test_str += f"  - Input Grid Size: {ttd['input_desc']['size']}\n"
            test_str += f"  - Colors Present: {ttd['input_desc']['colors']}\n"
            test_str += f"  - BLIP Description: {ttd['input_desc']['details']}\n\n"

        prompt = f"""
        [System note: Analyze the puzzle logically. Assume you see the grids based on their descriptions.]
        
        You have an ARC puzzle named '{task_name}'.
        Below are training examples, each with:
        - Grid size
        - Unique colors used
        - BLIP-generated description (if available)
        
        {train_str}
        {test_str}
        
        **Your Goal:** 
        1. Identify key transformations or rules from the training examples.
        2. Discuss potential patterns that could apply to the test examples.
        3. Predict the expected test output using logical reasoning.
        
        Structure your response clearly, step by step, and explain your thought process thoroughly.
        """
        return prompt.strip()

    def log_llm_solution(self, task_name, llm_text, success):
        """
        Store the raw LLM text in KG. 
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
        Old approach: if you still want it, we keep it, 
        but no JSON parse. We'll store text, success = False.
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
