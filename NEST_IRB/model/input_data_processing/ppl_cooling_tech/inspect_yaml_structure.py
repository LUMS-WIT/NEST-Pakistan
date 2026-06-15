import pandas as pd
import yaml
from pathlib import Path
import matplotlib.pyplot as plt

# ------------------------------------------------
# PATH TO YAML FILES
# ------------------------------------------------
base_input = Path(r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Indus Shape Files")

yaml_files = [
    base_input / "IRB.yaml"
]

# ------------------------------------------------
# FUNCTION TO ANALYZE YAML STRUCTURE
# ------------------------------------------------
def analyze_yaml(file_path):

    print("\n=================================")
    print("Reading:", file_path.name)
    print("=================================")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print("\nTop level nodes:")
    for node in data.keys():
        print("-", node)

    rows = []

    for region, content in data.items():

        if region == "World":
            continue

        children = content.get("child", [])

        for iso in children:
            rows.append({
                "region": region,
                "ISO": iso
            })

    df = pd.DataFrame(rows)

    print("\nSample mapping:")
    print(df.head())

    print("\nTotal regions:", df["region"].nunique())
    print("Total ISO codes:", df["ISO"].nunique())

    # ------------------------------------------------
    # Count children per region
    # ------------------------------------------------
    region_counts = (
        df.groupby("region")
        .size()
        .reset_index(name="num_children")
        .sort_values("num_children", ascending=False)
    )

    print("\nChildren per region:")
    print(region_counts)

    # ------------------------------------------------
    # Plot region sizes
    # ------------------------------------------------
    plt.figure(figsize=(10,6))

    plt.bar(
        region_counts["region"],
        region_counts["num_children"]
    )

    plt.title(f"Countries per Region ({file_path.stem})")
    plt.xlabel("Region")
    plt.ylabel("Number of ISO codes")

    plt.xticks(rotation=60)

    plt.tight_layout()
    plt.show()

    # ------------------------------------------------
    # Save flattened mapping
    # ------------------------------------------------
    output_csv = file_path.with_suffix(".csv")
    df.to_csv(output_csv, index=False)

    print("\nMapping saved to:", output_csv)


# ------------------------------------------------
# RUN FOR EACH YAML FILE
# ------------------------------------------------
for yaml_file in yaml_files:

    if yaml_file.exists():
        analyze_yaml(yaml_file)
    else:
        print("File not found:", yaml_file)

print("\nYAML inspection finished.")