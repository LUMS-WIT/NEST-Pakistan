import pandas as pd
import yaml
from pathlib import Path

csv_path = Path(r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Indus Shape Files\indus_bcu.csv")

df = pd.read_csv(csv_path)

df.columns = df.columns.str.strip().str.lower()

country_code_map = {
    "afghan": ("AFG", "afghanistan"),
    "pakistan": ("PAK", "pakistan"),
    "india": ("IND", "india"),
    "china": ("CHN", "china"),
    "indus": ("INDUS", "indus")
}

df["iso"] = None
df["region_clean"] = None

for idx, bcu in enumerate(df["bcu_id"]):

    name = str(bcu).lower()

    for key in country_code_map:

        if key in name:

            iso, region = country_code_map[key]

            df.loc[idx, "iso"] = iso
            df.loc[idx, "region_clean"] = region
            break

# --------------------------------
# BUILD YAML
# --------------------------------
regions = sorted(df["region_clean"].unique())

yaml_dict = {}

yaml_dict["World"] = {"child": regions}

for region in regions:

    iso_list = (
        df[df["region_clean"] == region]["iso"]
        .unique()
        .tolist()
    )

    yaml_dict[region] = {"child": iso_list}

# --------------------------------
# SAVE YAML
# --------------------------------
output_yaml = csv_path.parent / "IRB.yaml"

with open(output_yaml, "w") as f:
    yaml.dump(yaml_dict, f, sort_keys=False)

print("IRB.yaml created at:", output_yaml)