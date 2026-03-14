from django.db import migrations

BUILTIN_TEMPLATES = [
    {
        "name": "Circuit Testing",
        "slug": "circuit-testing",
        "description": "Template for electrical circuit testing and verification experiments.",
        "discipline": "electrical",
        "sections": [
            {"title": "Objective", "prompt": "State the purpose of the circuit test. What behaviour or parameter are you verifying?", "is_required": True, "order": 0},
            {"title": "Hypothesis", "prompt": "Predict the expected circuit behaviour, voltage levels, or current values before testing.", "is_required": True, "order": 1},
            {"title": "Components & Equipment", "prompt": "List all components (values, tolerances, part numbers) and test equipment (multimeter, oscilloscope, power supply) used.", "is_required": True, "order": 2},
            {"title": "Circuit Diagram", "prompt": "Attach or describe the schematic. Include pin assignments and any relevant annotations.", "is_required": True, "order": 3},
            {"title": "Procedure", "prompt": "Describe the step-by-step test procedure. Include safety precautions and power-on sequence.", "is_required": True, "order": 4},
            {"title": "Measurements & Results", "prompt": "Record all measured values, waveforms, and observations. Include units and instrument settings.", "is_required": True, "order": 5},
            {"title": "Analysis", "prompt": "Compare measured results to expected values. Explain any discrepancies or anomalies.", "is_required": True, "order": 6},
            {"title": "Conclusion", "prompt": "Did the circuit meet the test criteria? What follow-up actions or design changes are required?", "is_required": True, "order": 7},
        ],
    },
    {
        "name": "Materials Testing",
        "slug": "materials-testing",
        "description": "Template for mechanical and physical properties testing of materials.",
        "discipline": "materials",
        "sections": [
            {"title": "Objective", "prompt": "State the material property being tested (e.g. tensile strength, hardness, fatigue limit) and the reason for testing.", "is_required": True, "order": 0},
            {"title": "Hypothesis", "prompt": "Predict the expected material behaviour based on published data or prior knowledge.", "is_required": True, "order": 1},
            {"title": "Materials & Specimens", "prompt": "Describe the material, grade, supplier, specimen geometry, and any pre-treatment (heat treatment, surface finish).", "is_required": True, "order": 2},
            {"title": "Equipment", "prompt": "List the testing machine, load cell, extensometer, and any other instruments. Include calibration dates.", "is_required": True, "order": 3},
            {"title": "Test Procedure", "prompt": "Describe the test standard followed (e.g. ASTM, ISO), loading rate, environmental conditions, and step-by-step procedure.", "is_required": True, "order": 4},
            {"title": "Observations", "prompt": "Record visual observations during testing (cracking, necking, surface changes). Note any anomalies.", "is_required": True, "order": 5},
            {"title": "Results & Data", "prompt": "Present raw data, stress-strain curves, load-displacement plots, or tabulated results. Include units.", "is_required": True, "order": 6},
            {"title": "Analysis", "prompt": "Calculate derived properties (Young's modulus, yield strength, UTS). Compare to specification. Discuss failure modes.", "is_required": True, "order": 7},
            {"title": "Conclusion", "prompt": "Does the material meet the required specification? What are the implications for design or material selection?", "is_required": True, "order": 8},
        ],
    },
    {
        "name": "Fluid Mechanics",
        "slug": "fluid-mechanics",
        "description": "Template for fluid mechanics experiments covering flow, pressure, and viscosity.",
        "discipline": "fluids",
        "sections": [
            {"title": "Objective", "prompt": "Define the fluid phenomenon being studied (e.g. pipe flow, drag, Bernoulli effect) and the measurement goal.", "is_required": True, "order": 0},
            {"title": "Hypothesis", "prompt": "State the predicted relationship between variables based on fluid theory or governing equations.", "is_required": True, "order": 1},
            {"title": "Apparatus", "prompt": "Describe the test rig, flow loop, tank, pump, valves, and instrumentation. Attach a schematic if available.", "is_required": True, "order": 2},
            {"title": "Fluid Properties", "prompt": "Record the fluid used, temperature, density, dynamic viscosity, and any relevant thermodynamic properties.", "is_required": True, "order": 3},
            {"title": "Experimental Procedure", "prompt": "Describe the step-by-step procedure: startup sequence, flow rate settings, stabilisation time, and data recording steps.", "is_required": True, "order": 4},
            {"title": "Measurements", "prompt": "Record all pressure readings, flow rates, velocities, temperatures, and timing data. Include instrument uncertainty.", "is_required": True, "order": 5},
            {"title": "Results", "prompt": "Present processed results: Reynolds number, flow coefficients, head loss, or dimensionless groups as applicable.", "is_required": True, "order": 6},
            {"title": "Analysis", "prompt": "Compare experimental results to theoretical predictions. Discuss sources of error and their magnitude.", "is_required": True, "order": 7},
            {"title": "Conclusion", "prompt": "Summarise the key findings. Do results validate the hypothesis? What improvements would increase accuracy?", "is_required": True, "order": 8},
        ],
    },
    {
        "name": "Structural Analysis",
        "slug": "structural-analysis",
        "description": "Template for structural loading, deflection, and failure analysis experiments.",
        "discipline": "structural",
        "sections": [
            {"title": "Objective", "prompt": "State the structural behaviour being investigated (e.g. beam deflection, column buckling, joint strength).", "is_required": True, "order": 0},
            {"title": "Hypothesis", "prompt": "Predict the structural response using beam theory, FEA, or hand calculations. State assumptions.", "is_required": True, "order": 1},
            {"title": "Materials & Specimens", "prompt": "Describe the specimen material, cross-section geometry, dimensions, and any pre-existing conditions or defects.", "is_required": True, "order": 2},
            {"title": "Loading Conditions", "prompt": "Describe the load type (point, distributed, cyclic), boundary conditions, and support arrangement.", "is_required": True, "order": 3},
            {"title": "Test Procedure", "prompt": "Step-by-step procedure for applying loads, recording deflections, and observing failure. Note safety limits.", "is_required": True, "order": 4},
            {"title": "Observations", "prompt": "Describe visual observations during loading: cracking, yielding, deformation patterns, failure location.", "is_required": True, "order": 5},
            {"title": "Results", "prompt": "Present load-deflection plots, strain gauge readings, and failure load. Compare to theoretical predictions.", "is_required": True, "order": 6},
            {"title": "Analysis", "prompt": "Quantify error between experiment and theory. Discuss assumptions that may have contributed to discrepancies.", "is_required": True, "order": 7},
            {"title": "Conclusion", "prompt": "Did the structure behave as predicted? What does this mean for design allowables or safety factors?", "is_required": True, "order": 8},
        ],
    },
    {
        "name": "Software Test Log",
        "slug": "software-test-log",
        "description": "Template for logging software test execution, defects, and outcomes.",
        "discipline": "software",
        "sections": [
            {"title": "Objective", "prompt": "Describe the feature, module, or system under test and the goal of this test session.", "is_required": True, "order": 0},
            {"title": "Test Environment", "prompt": "Record OS, browser/runtime version, database version, build number, and any environment-specific configuration.", "is_required": True, "order": 1},
            {"title": "Test Cases", "prompt": "List each test case with: ID, description, preconditions, input data, and expected outcome.", "is_required": True, "order": 2},
            {"title": "Execution Log", "prompt": "For each test case, record: actual outcome, pass/fail status, and timestamp of execution.", "is_required": True, "order": 3},
            {"title": "Defects Found", "prompt": "Document each defect: ID, severity, steps to reproduce, actual vs expected behaviour, and linked test case.", "is_required": False, "order": 4},
            {"title": "Results Summary", "prompt": "Summarise total tests run, passed, failed, and blocked. Include pass rate and any risk assessment.", "is_required": True, "order": 5},
            {"title": "Conclusion", "prompt": "Is the feature ready to proceed? What follow-up actions or re-tests are required before sign-off?", "is_required": True, "order": 6},
        ],
    },
    {
        "name": "Field Observation",
        "slug": "field-observation",
        "description": "Template for recording on-site field observations, inspections, and environmental measurements.",
        "discipline": "field_observation",
        "sections": [
            {"title": "Objective", "prompt": "State the purpose of the site visit or field observation. What are you assessing or measuring?", "is_required": True, "order": 0},
            {"title": "Location & Conditions", "prompt": "Record site name, GPS coordinates or address, date, time, weather conditions, and ambient temperature.", "is_required": True, "order": 1},
            {"title": "Equipment Used", "prompt": "List all field instruments, sampling tools, PPE, and any data loggers used during the observation.", "is_required": True, "order": 2},
            {"title": "Observations", "prompt": "Describe qualitative observations: site conditions, visible anomalies, structural state, or environmental indicators.", "is_required": True, "order": 3},
            {"title": "Measurements", "prompt": "Record all quantitative measurements with units, instrument IDs, and calibration status.", "is_required": True, "order": 4},
            {"title": "Photographs & Sketches", "prompt": "Attach or reference photographs, sketches, or annotated diagrams taken on site.", "is_required": False, "order": 5},
            {"title": "Analysis", "prompt": "Interpret observations and measurements. Compare to baseline, design intent, or regulatory limits.", "is_required": True, "order": 6},
            {"title": "Conclusion", "prompt": "Summarise findings. Are any immediate actions, follow-up visits, or escalations required?", "is_required": True, "order": 7},
        ],
    },
]


def seed_templates(apps, schema_editor):
    EntryTemplate = apps.get_model("templates_engine", "EntryTemplate")
    TemplateSection = apps.get_model("templates_engine", "TemplateSection")

    for tmpl_data in BUILTIN_TEMPLATES:
        sections = tmpl_data.pop("sections")
        tmpl = EntryTemplate.objects.create(is_builtin=True, **tmpl_data)
        TemplateSection.objects.bulk_create([
            TemplateSection(template=tmpl, **section)
            for section in sections
        ])


def unseed_templates(apps, schema_editor):
    EntryTemplate = apps.get_model("templates_engine", "EntryTemplate")
    EntryTemplate.objects.filter(is_builtin=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("templates_engine", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(seed_templates, reverse_code=unseed_templates),
    ]
