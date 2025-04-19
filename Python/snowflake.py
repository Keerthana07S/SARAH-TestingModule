import pandas as pd
import numpy as np
import snowflake.connector

conn = snowflake.connector.connect(
    user="your_username",
    password="your_password",
    account="your_account",
    role="your_role",
    warehouse="your_warehouse",
    database="your_database",
    schema="your_schema",
)

cursor = conn.cursor()

def simulate_50_nodes():
    data = []

    for i in range(50):
        node_id = f"Node_{i+1}"
        
        Isc = np.random.uniform(30, 35)  
        G = np.random.uniform(600, 1000) 

        fault_type = "None"

        if np.random.rand() < 0.2:
            Isc = np.random.uniform(40, 50)
            fault_type = "High_Isc"

        if np.random.rand() < 0.2:
            G = np.random.uniform(1500, 2000)
            fault_type = fault_type if fault_type != "None" else "High_G"
            if "High_Isc" in fault_type:
                fault_type += "+High_G"

        data.append({
            "NodeID": node_id,
            "Isc_mA": round(Isc, 2),
            "Radiation_G_W_per_m2": round(G, 2),
            "Fault_Type": fault_type
        })

    return pd.DataFrame(data)

def upload_to_snowflake(df, table_name="VIRTUAL_NODES"):
    cursor.execute(f"""
        CREATE OR REPLACE TABLE {table_name} (
            NodeID STRING,
            Isc_mA FLOAT,
            Radiation_G_W_per_m2 FLOAT,
            Fault_Type STRING
        )
    """)

    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {table_name} (NodeID, Isc_mA, Radiation_G_W_per_m2, Fault_Type)
            VALUES (%s, %s, %s, %s)
        """, (row["NodeID"], row["Isc_mA"], row["Radiation_G_W_per_m2"], row["Fault_Type"]))

if __name__ == "__main__":
    df_nodes = simulate_50_nodes()
    print("Simulated Node Data:\n", df_nodes.head())
    upload_to_snowflake(df_nodes)
    print("50 virtual nodes uploaded to Snowflake successfully.")

    cursor.close()
    conn.close()
