"""Disease knowledge base (English + Kannada).

These are the defaults loaded into the database. An admin can edit them later
from the Admin page. Advice is deliberately general: it tells the farmer what
to look for and what to do first, and always points to an expert for
chemical/dose decisions. Have an agriculture officer review before real use.
Kannada text should be reviewed by a native speaker.
"""

DISEASES = {
    "healthy": {
        "name": {"en": "Healthy", "kn": "ಆರೋಗ್ಯಕರ"},
        "part": {"en": "Leaf / nut / trunk", "kn": "ಎಲೆ / ಅಡಿಕೆ / ಕಾಂಡ"},
        "severity": "none",
        "symptoms": {
            "en": "No visible signs of disease or pest damage in this photo.",
            "kn": "ಈ ಫೋಟೋದಲ್ಲಿ ರೋಗ ಅಥವಾ ಕೀಟದ ಹಾನಿಯ ಯಾವುದೇ ಲಕ್ಷಣ ಕಾಣುತ್ತಿಲ್ಲ.",
        },
        "recommendation": {
            "en": "Keep up regular care: proper drainage, balanced manure, and weekly checking of leaves, bunches and trunk. Check again if you notice any change.",
            "kn": "ನಿಯಮಿತ ಆರೈಕೆ ಮುಂದುವರಿಸಿ: ಸರಿಯಾದ ನೀರು ಹರಿವು, ಸಮತೋಲನ ಗೊಬ್ಬರ, ಮತ್ತು ವಾರಕ್ಕೊಮ್ಮೆ ಎಲೆ, ಗೊನೆ ಮತ್ತು ಕಾಂಡ ಪರಿಶೀಲನೆ. ಯಾವುದೇ ಬದಲಾವಣೆ ಕಂಡರೆ ಮತ್ತೆ ಪರೀಕ್ಷಿಸಿ.",
        },
        "prevention": {
            "en": "Avoid water-logging, avoid injuring the trunk, keep the garden clean.",
            "kn": "ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ, ಕಾಂಡಕ್ಕೆ ಗಾಯ ಮಾಡಬೇಡಿ, ತೋಟ ಸ್ವಚ್ಛವಾಗಿಡಿ.",
        },
    },
    "mahali_koleroga": {
        "name": {"en": "Mahali / Koleroga (Fruit Rot)", "kn": "ಮಹಾಳಿ / ಕೊಳೆರೋಗ"},
        "part": {"en": "Nut / bunch", "kn": "ಅಡಿಕೆ / ಗೊನೆ"},
        "severity": "high",
        "symptoms": {
            "en": "Water-soaked dark patches on young nuts that turn black and rot. Nuts may fall off. Common in the rainy season.",
            "kn": "ಎಳೆ ಅಡಿಕೆಯ ಮೇಲೆ ನೀರು ತುಂಬಿದಂತಹ ಕಪ್ಪು ಕಲೆಗಳು, ನಂತರ ಕಪ್ಪಾಗಿ ಕೊಳೆಯುತ್ತವೆ. ಅಡಿಕೆ ಉದುರಬಹುದು. ಮಳೆಗಾಲದಲ್ಲಿ ಹೆಚ್ಚು.",
        },
        "recommendation": {
            "en": "Remove and destroy fallen and infected nuts and bunches away from the garden. Spraying a 1% Bordeaux mixture on bunches is the usual protection, ideally before heavy rain and repeated as advised locally. Improve drainage. Show the photo to your Horticulture officer or Krishi Vigyan Kendra for exact timing.",
            "kn": "ಉದುರಿದ ಮತ್ತು ರೋಗಪೀಡಿತ ಅಡಿಕೆ ಹಾಗೂ ಗೊನೆಗಳನ್ನು ತೋಟದಿಂದ ದೂರ ತೆಗೆದು ನಾಶಮಾಡಿ. ಗೊನೆಗಳಿಗೆ ಶೇ.1 ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಣೆ ಸಾಮಾನ್ಯ ರಕ್ಷಣೆ; ಭಾರೀ ಮಳೆಗೆ ಮೊದಲು ಮಾಡಿ, ಸ್ಥಳೀಯ ಸಲಹೆಯಂತೆ ಪುನರಾವರ್ತಿಸಿ. ನೀರು ಹರಿವು ಸುಧಾರಿಸಿ. ಸರಿಯಾದ ಸಮಯಕ್ಕಾಗಿ ತೋಟಗಾರಿಕೆ ಅಧಿಕಾರಿ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        },
        "prevention": {
            "en": "Spray before the monsoon, keep the garden open to air and sunlight, clear fallen nuts regularly.",
            "kn": "ಮಳೆಗಾಲಕ್ಕೆ ಮೊದಲು ಸಿಂಪಡಿಸಿ, ತೋಟದಲ್ಲಿ ಗಾಳಿ ಬೆಳಕು ಇರುವಂತೆ ನೋಡಿ, ಉದುರಿದ ಅಡಿಕೆಯನ್ನು ಆಗಾಗ ತೆಗೆದುಹಾಕಿ.",
        },
    },
    "yellow_leaf_disease": {
        "name": {"en": "Yellow Leaf Disease", "kn": "ಹಳದಿ ಎಲೆ ರೋಗ"},
        "part": {"en": "Leaf", "kn": "ಎಲೆ"},
        "severity": "high",
        "symptoms": {
            "en": "Leaves turn yellow, usually starting at the tips, then dry up. Crown shrinks and nut yield drops over time.",
            "kn": "ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತವೆ, ಸಾಮಾನ್ಯವಾಗಿ ತುದಿಯಿಂದ ಪ್ರಾರಂಭ, ನಂತರ ಒಣಗುತ್ತವೆ. ಮರದ ತಲೆ ಚಿಕ್ಕದಾಗಿ ಇಳುವರಿ ಕಡಿಮೆಯಾಗುತ್ತದೆ.",
        },
        "recommendation": {
            "en": "There is no quick cure. Give proper irrigation and balanced nutrition to keep palms stronger, and avoid planting new palms near badly affected ones. Report the garden to the Horticulture department or a research centre (e.g. CPCRI) so the palms can be examined. Yellowing can also come from nutrient or water problems, so get it confirmed.",
            "kn": "ತ್ವರಿತ ಚಿಕಿತ್ಸೆ ಇಲ್ಲ. ಮರಗಳು ಬಲವಾಗಿರಲು ಸರಿಯಾದ ನೀರಾವರಿ ಮತ್ತು ಸಮತೋಲನ ಪೋಷಕಾಂಶ ನೀಡಿ; ತೀವ್ರ ಬಾಧಿತ ಮರಗಳ ಬಳಿ ಹೊಸ ಸಸಿ ನೆಡಬೇಡಿ. ಮರಗಳ ಪರೀಕ್ಷೆಗಾಗಿ ತೋಟಗಾರಿಕೆ ಇಲಾಖೆ ಅಥವಾ ಸಂಶೋಧನಾ ಕೇಂದ್ರಕ್ಕೆ (ಉದಾ. ಸಿಪಿಸಿಆರ್‌ಐ) ತಿಳಿಸಿ. ಹಳದಿ ಬಣ್ಣ ಪೋಷಕಾಂಶ ಅಥವಾ ನೀರಿನ ಸಮಸ್ಯೆಯಿಂದಲೂ ಬರಬಹುದು, ಆದ್ದರಿಂದ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
        },
        "prevention": {
            "en": "Regular irrigation, balanced manure, use healthy planting material.",
            "kn": "ನಿಯಮಿತ ನೀರಾವರಿ, ಸಮತೋಲನ ಗೊಬ್ಬರ, ಆರೋಗ್ಯಕರ ಸಸಿಗಳನ್ನು ಬಳಸಿ.",
        },
    },
    "stem_bleeding": {
        "name": {"en": "Stem Bleeding", "kn": "ಕಾಂಡ ರಕ್ತಸ್ರಾವ"},
        "part": {"en": "Trunk", "kn": "ಕಾಂಡ"},
        "severity": "medium",
        "symptoms": {
            "en": "Reddish-brown liquid oozes from the trunk and dries to a dark stain. The tissue underneath may be rotten.",
            "kn": "ಕಾಂಡದಿಂದ ಕೆಂಪು-ಕಂದು ದ್ರವ ಸೋರುತ್ತದೆ ಮತ್ತು ಒಣಗಿ ಕಪ್ಪು ಕಲೆಯಾಗುತ್ತದೆ. ಒಳಗಿನ ಭಾಗ ಕೊಳೆತಿರಬಹುದು.",
        },
        "recommendation": {
            "en": "Carefully scrape out the rotten tissue, then apply a protective paste such as Bordeaux paste or coal tar on the cut area. Do not wound the trunk further. Improve drainage and avoid water standing at the base. Ask a Horticulture officer about any soil treatment.",
            "kn": "ಕೊಳೆತ ಭಾಗವನ್ನು ಜಾಗರೂಕತೆಯಿಂದ ಕೆರೆದು ತೆಗೆದು, ಆ ಜಾಗಕ್ಕೆ ಬೋರ್ಡೋ ಪೇಸ್ಟ್ ಅಥವಾ ಕೋಲ್ ಟಾರ್ ಹಚ್ಚಿ. ಕಾಂಡಕ್ಕೆ ಹೆಚ್ಚಿನ ಗಾಯ ಮಾಡಬೇಡಿ. ನೀರು ಹರಿವು ಸುಧಾರಿಸಿ, ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿ. ಮಣ್ಣಿನ ಚಿಕಿತ್ಸೆಗಾಗಿ ತೋಟಗಾರಿಕೆ ಅಧಿಕಾರಿಯನ್ನು ಕೇಳಿ.",
        },
        "prevention": {
            "en": "Avoid trunk injuries while working, keep drainage clear.",
            "kn": "ಕೆಲಸ ಮಾಡುವಾಗ ಕಾಂಡಕ್ಕೆ ಗಾಯವಾಗದಂತೆ ನೋಡಿ, ನೀರು ಹರಿವು ಸರಿಯಾಗಿರಲಿ.",
        },
    },
    "bud_borer": {
        "name": {"en": "Bud Borer (Pest)", "kn": "ಮೊಗ್ಗು ಕೊರೆಯುವ ಕೀಟ"},
        "part": {"en": "Crown / bud", "kn": "ತಲೆ / ಮೊಗ್ಗು"},
        "severity": "high",
        "symptoms": {
            "en": "Damage or holes in the growing bud or youngest leaves; the central spindle may look chewed, rotten or dried.",
            "kn": "ಬೆಳೆಯುತ್ತಿರುವ ಮೊಗ್ಗು ಅಥವಾ ಎಳೆ ಎಲೆಗಳಲ್ಲಿ ಹಾನಿ ಅಥವಾ ರಂಧ್ರಗಳು; ಮಧ್ಯದ ಸುಳಿ ತಿಂದಂತೆ, ಕೊಳೆತಂತೆ ಅಥವಾ ಒಣಗಿದಂತೆ ಕಾಣಬಹುದು.",
        },
        "recommendation": {
            "en": "This can kill the palm, so act quickly. Contact your Horticulture officer or Krishi Vigyan Kendra the same week for the correct pesticide and dose. Use pesticides only as per the label and wear protection. Remove and destroy badly damaged parts.",
            "kn": "ಇದು ಮರವನ್ನೇ ಸಾಯಿಸಬಹುದು, ಆದ್ದರಿಂದ ಬೇಗ ಕ್ರಮ ಕೈಗೊಳ್ಳಿ. ಸರಿಯಾದ ಕೀಟನಾಶಕ ಮತ್ತು ಪ್ರಮಾಣಕ್ಕಾಗಿ ಅದೇ ವಾರ ತೋಟಗಾರಿಕೆ ಅಧಿಕಾರಿ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು ಸಂಪರ್ಕಿಸಿ. ಲೇಬಲ್‌ನಲ್ಲಿರುವಂತೆ ಮಾತ್ರ ಕೀಟನಾಶಕ ಬಳಸಿ, ರಕ್ಷಣಾ ಉಡುಪು ಧರಿಸಿ. ತೀವ್ರ ಹಾನಿಗೊಂಡ ಭಾಗಗಳನ್ನು ತೆಗೆದು ನಾಶಮಾಡಿ.",
        },
        "prevention": {
            "en": "Inspect the crown regularly, remove dead material, keep the garden clean.",
            "kn": "ತಲೆಯ ಭಾಗವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ, ಸತ್ತ ಭಾಗಗಳನ್ನು ತೆಗೆಯಿರಿ, ತೋಟ ಸ್ವಚ್ಛವಾಗಿಡಿ.",
        },
    },
    "stem_cracking": {
        "name": {"en": "Stem Cracking", "kn": "ಕಾಂಡ ಬಿರುಕು"},
        "part": {"en": "Trunk", "kn": "ಕಾಂಡ"},
        "severity": "low",
        "symptoms": {
            "en": "Vertical splits or cracks on the trunk. Often linked to uneven watering or nutrient imbalance rather than an infection.",
            "kn": "ಕಾಂಡದ ಮೇಲೆ ಉದ್ದವಾದ ಬಿರುಕುಗಳು. ಸೋಂಕಿಗಿಂತ ಹೆಚ್ಚಾಗಿ ಅಸಮ ನೀರಾವರಿ ಅಥವಾ ಪೋಷಕಾಂಶದ ಅಸಮತೋಲನದಿಂದ ಬರುತ್ತದೆ.",
        },
        "recommendation": {
            "en": "Water regularly instead of long dry gaps followed by heavy watering. Mulch around the base and use balanced manure. A soil test will show if a micronutrient such as boron is lacking. Watch the cracks for oozing or rot, which would need a different check.",
            "kn": "ಬಹಳ ದಿನ ಒಣಗಿಸಿ ನಂತರ ಹೆಚ್ಚು ನೀರು ಕೊಡುವ ಬದಲು ನಿಯಮಿತವಾಗಿ ನೀರು ಕೊಡಿ. ಬುಡದ ಸುತ್ತ ಮುಚ್ಚಿಗೆ ಹಾಕಿ ಮತ್ತು ಸಮತೋಲನ ಗೊಬ್ಬರ ಬಳಸಿ. ಬೋರಾನ್‌ನಂತಹ ಲಘು ಪೋಷಕಾಂಶ ಕೊರತೆ ಇದೆಯೇ ಎಂದು ಮಣ್ಣು ಪರೀಕ್ಷೆ ತೋರಿಸುತ್ತದೆ. ಬಿರುಕಿನಲ್ಲಿ ಸೋರುವಿಕೆ ಅಥವಾ ಕೊಳೆತ ಕಂಡರೆ ಬೇರೆ ಪರೀಕ್ಷೆ ಬೇಕು.",
        },
        "prevention": {
            "en": "Steady irrigation, mulching, balanced nutrition.",
            "kn": "ಸ್ಥಿರ ನೀರಾವರಿ, ಮುಚ್ಚಿಗೆ, ಸಮತೋಲನ ಪೋಷಕಾಂಶ.",
        },
    },
}

SEVERITY_LABEL = {
    "none": {"en": "No problem found", "kn": "ಸಮಸ್ಯೆ ಇಲ್ಲ"},
    "low": {"en": "Low urgency", "kn": "ಕಡಿಮೆ ತುರ್ತು"},
    "medium": {"en": "Act soon", "kn": "ಶೀಘ್ರ ಕ್ರಮ ಬೇಕು"},
    "high": {"en": "Act urgently", "kn": "ತುರ್ತು ಕ್ರಮ ಬೇಕು"},
}
