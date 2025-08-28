import pandas as pd
import glob
import os

data_path = os.path.join("data", "*.csv")
all_files = glob.glob(data_path)
df_list = [pd.read_csv(file) for file in all_files]
df = pd.concat(df_list, ignore_index=True)

df = df[df["product"].str.lower() == "pink morsel"]

df["price"] = df["price"].replace('[\$,]', '', regex=True).astype(float)
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

df["sales"] = df["quantity"] * df["price"]

output_df = df[["sales", "date", "region"]]
output_df.to_csv("output.csv", index=False)

print(output_df.head(20).to_string(index=False))
print("✅ Output saved as output.csv")
