"""
Script to generate synthetic datasets for GETTSIM benchmarking/profiling.

"""
# %%

import pandas as pd
import numpy as np
import time

def make_data(N):
    """
    Create a DataFrame with N households, each containing 2 parents and 2 children.
    Uses vectorized operations for fast data generation.
    
    Parameters:
    N (int): Number of households to create
    
    Returns:
    pd.DataFrame: DataFrame with household data (4*N rows)
    """
    # Total number of people (4 per household: 2 parents + 2 children)
    total_people = N * 4
    
    # Create base template for one household (4 people)
    base_template = np.array([
        # Parent 1
        [30, 35, 0, 1995, 0, 0, False, False, 0, 0, 5000, 0, 500, 0, 0, 0, 0, -1, True, 0, 0, True, False, False, 1, -1, -1, False, -1],
        # Parent 2  
        [30, 35, 0, 1995, 0, 1, False, False, 0, 0, 4000, 0, 0, 0, 0, 0, 0, -1, True, 0, 0, True, False, False, 0, -1, -1, False, -1],
        # Child 1
        [10, 0, 0, 2015, 0, 2, False, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False, 0, 0, False, False, True, -1, 0, 1, False, 0],
        # Child 2 (twin)
        [10, 0, 0, 2015, 0, 3, False, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False, 0, 0, False, False, True, -1, 0, 1, False, 0]
    ])
    
    # Replicate template for all households
    data_array = np.tile(base_template, (N, 1))
    
    # Create household and person IDs using vectorized operations
    hh_ids = np.repeat(np.arange(N), 4)
    p_ids = np.arange(total_people)
    
    # Update IDs in the data array
    data_array[:, 4] = hh_ids  # hh_id column
    data_array[:, 5] = p_ids   # p_id column
    
    # Update spouse_ids for parents (every 4th person starting from 0 gets spouse_id of next person, and vice versa)
    spouse_mask_1 = np.arange(total_people) % 4 == 0  # Parent 1 positions
    spouse_mask_2 = np.arange(total_people) % 4 == 1  # Parent 2 positions
    data_array[spouse_mask_1, 24] = p_ids[spouse_mask_1] + 1  # Parent 1 -> Parent 2
    data_array[spouse_mask_2, 24] = p_ids[spouse_mask_2] - 1  # Parent 2 -> Parent 1
    
    # Update parent_ids for children
    child_mask_1 = np.arange(total_people) % 4 == 2  # Child 1 positions
    child_mask_2 = np.arange(total_people) % 4 == 3  # Child 2 positions
    parent1_ids = p_ids[child_mask_1] - 2  # Parent 1 IDs for children
    parent2_ids = p_ids[child_mask_1] - 1  # Parent 2 IDs for children
    
    data_array[child_mask_1, 25] = parent1_ids  # parent_id_1 for child 1
    data_array[child_mask_1, 26] = parent2_ids  # parent_id_2 for child 1
    data_array[child_mask_2, 25] = parent1_ids  # parent_id_1 for child 2 
    data_array[child_mask_2, 26] = parent2_ids  # parent_id_2 for child 2
    
    # Update person_that_pays_childcare_expenses and id_recipient_child_allowance for children
    data_array[child_mask_1, 11] = parent1_ids  # person_that_pays_childcare_expenses for child 1
    data_array[child_mask_2, 11] = parent1_ids  # person_that_pays_childcare_expenses for child 2
    data_array[child_mask_1, 28] = parent1_ids  # id_recipient_child_allowance for child 1
    data_array[child_mask_2, 28] = parent1_ids  # id_recipient_child_allowance for child 2
    
    # Column names in the same order as the template
    columns = [
        "age", "working_hours", "disability_grade", "birth_year", "hh_id", "p_id",
        "east_germany", "self_employed", "income_from_self_employment", "income_from_rent",
        "income_from_employment", "income_from_forest_and_agriculture", "income_from_capital",
        "income_from_other_sources", "pension_income", "contribution_to_private_pension_insurance",
        "childcare_expenses", "person_that_pays_childcare_expenses", "joint_taxation",
        "amount_private_pension_income", "contribution_private_health_insurance", "has_children",
        "single_parent", "is_child", "spouse_id", "parent_id_1", "parent_id_2", "in_training",
        "id_recipient_child_allowance"
    ]
    
    # Create DataFrame
    data = pd.DataFrame(data_array, columns=columns)
    
    # Convert boolean columns back to bool (they become float during array operations)
    bool_columns = ["east_germany", "self_employed", "joint_taxation", "has_children", "single_parent", "is_child", "in_training"]
    for col in bool_columns:
        data[col] = data[col].astype(bool)
    
    # Convert integer columns to int
    int_columns = ["age", "working_hours", "disability_grade", "birth_year", "hh_id", "p_id", 
                   "spouse_id", "parent_id_1", "parent_id_2", "person_that_pays_childcare_expenses", 
                   "id_recipient_child_allowance"]
    for col in int_columns:
        data[col] = data[col].astype(int)
    
    print(f"Created DataFrame with {len(data)} rows ({len(data) // 4} households)")
    return data


def main():
    """Generate datasets for all required sizes and measure timing."""
    # Dataset sizes (number of households)
    # Each household has 4 people (2 parents + 2 children)
    household_sizes = [2**15-1, 2**15, 2**16, 2**17, 2**18, 2**19, 2**20]
    
    print("Generating synthetic datasets for GETTSIM benchmarking...")
    print("=" * 60)
    
    timing_results = []
    
    for num_households in household_sizes:
        print(f"\nGenerating dataset for {num_households:,} households...")
        
        # Time the data creation
        start_time = time.time()
        data = make_data(num_households)
        end_time = time.time()
        
        creation_time = end_time - start_time
        timing_results.append((num_households, creation_time))
        
        # Calculate memory usage estimation
        memory_mb = data.memory_usage(deep=True).sum() / (1024 * 1024)
        
        print(f"✓ Created {num_households:,} households ({len(data):,} people) in {creation_time:.3f} seconds")
        print(f"  Memory usage: {memory_mb:.2f} MB")
        print(f"  Speed: {num_households / creation_time:.0f} households/second")

    print("\n" + "=" * 60)
    print("Performance Summary:")
    print("=" * 60)
    print(f"{'Households':<12} {'Time (s)':<10} {'Speed (hh/s)':<15} {'People':<10}")
    print("-" * 60)
    
    for num_households, creation_time in timing_results:
        speed = num_households / creation_time
        people = num_households * 4
        print(f"{num_households:<12,} {creation_time:<10.3f} {speed:<15,.0f} {people:<10,}")
    
    print("\nDataset generation completed successfully!")
    print("Note: Data is held in memory only - no files saved to disk.")


if __name__ == "__main__":
    main()

# %%
# For inspection:
# example_data = make_data(3)  # 3 households = 12 people

