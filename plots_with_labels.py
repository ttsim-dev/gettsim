#%%
"""
Script to generate DAG plots with visible node labels.
Extracted from PR32.py for better organization.
"""

from pathlib import Path
import mettsim.middle_earth as middle_earth
from ttsim.plot import dag
from ttsim.main_args import Labels


def add_visible_labels(fig):
    """Add visible text labels to DAG plot nodes with FULL node names."""
    for i, trace in enumerate(fig.data):
        # Find the node trace (it has markers and text)
        if (hasattr(trace, 'mode') and 
            hasattr(trace, 'text') and 
            trace.mode == 'markers' and 
            trace.text is not None):
            
            # Change mode to show both markers and text
            trace.mode = 'markers+text'
            trace.textposition = 'middle center'
            
            # Add text font settings to ensure proper rendering
            trace.textfont = dict(size=10, family="Arial")
            
            # Convert tuple to list if needed
            text_list = list(trace.text) if isinstance(trace.text, tuple) else trace.text
            
            # Process the text to show FULL labels
            full_labels = []
            for text in text_list:
                if isinstance(text, str):
                    # Keep HTML line breaks for multi-line labels in Plotly
                    if '<br>' in text:
                        # Keep the <br> tags as they work better in Plotly
                        full_label = text
                    else:
                        full_label = text
                        
                    full_labels.append(full_label)
                else:
                    full_labels.append(str(text))
                    
            # Convert back to tuple if original was tuple
            if isinstance(trace.text, tuple):
                trace.text = tuple(full_labels)
            else:
                trace.text = full_labels
    
    return fig


def main():
    """Generate DAG plots with visible labels."""
    
    # Plot 1: Ancestors plot
    print("Generating Ancestors Plot...")
    fig = dag.tt(
        root=middle_earth.ROOT_PATH,
        policy_date_str="2000-01-01",
        primary_nodes={"orc_hunting_bounty__amount"},
        labels=Labels(input_columns={"orc_hunting_bounty__amount_without_topup"}),
        selection_type="ancestors",
        include_params=False,
        title="Ancestors Plot: orc_hunting_bounty__amount"
    )
    fig = add_visible_labels(fig)
    fig.write_html(Path("ancestors_with_labels.html"))
    fig.write_image(Path("ancestors_with_labels.svg"))
    print("Saved: ancestors_with_labels.html and ancestors_with_labels.svg")

    # Plot 2: Descendants plot
    print("Generating Descendants Plot...")
    fig = dag.tt(
        root=middle_earth.ROOT_PATH,
        policy_date_str="2000-01-01",
        primary_nodes={"orc_hunting_bounty__amount_without_topup"},
        labels=Labels(input_columns={"orc_hunting_bounty__amount"}),
        selection_type="descendants",
        include_params=False,
        title="Descendants Plot: orc_hunting_bounty__amount_without_topup"
    )
    fig = add_visible_labels(fig)
    fig.write_html(Path("descendants_with_labels.html"))
    fig.write_image(Path("descendants_with_labels.svg"))
    print("Saved: descendants_with_labels.html and descendants_with_labels.svg")
    
    print("Plot generation completed!")


if __name__ == "__main__":
    main()

# %%
