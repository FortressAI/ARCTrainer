from pyswip import Prolog
import os

prolog = Prolog()

# Print the detected SWI-Prolog path
swipl_path = os.environ.get("SWI_PROLOG", "Not Set")
print(f"📌 Detected SWI-Prolog Path: {swipl_path}")

try:
    print("📌 Attempting to consult Prolog file...")
    prolog.consult("/Users/richardgillespie/Documents/ARC_Trainer/ARC_Trainer/prolog_rules/prolog_engine.pl")
    print("✅ Prolog engine loaded successfully!")

    # Run a test query
    result = list(prolog.query("true."))
    print("✅ Query returned:", result)

except StopIteration:
    print("⚠️ StopIteration Error: No response from Prolog. Try restarting Python.")
    raise RuntimeError("PySWIP encountered a StopIteration error.")

except Exception as e:
    print(f"❌ Other Error: {e}")
