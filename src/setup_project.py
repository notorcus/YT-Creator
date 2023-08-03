import os, config

def setup_project(project_name):
    base_dir = "projects" 
    config.project_dir = os.path.join(base_dir, project_name)
    config.transcript_folder = os.path.join(config.project_dir, "intermediate", "transcripts")
    
    # Create input directory
    input_dir = os.path.join(config.project_dir, "input")
    os.makedirs(input_dir, exist_ok=True)

    # Create intermediate directories
    intermediate_dir = os.path.join(config.project_dir, "intermediate")
    os.makedirs(os.path.join(intermediate_dir, "cutstamps"), exist_ok=True)
    os.makedirs(os.path.join(intermediate_dir, "transcripts"), exist_ok=True)

    # Create final output directory
    final_output_dir = os.path.join(config.project_dir, "final_output")
    os.makedirs(final_output_dir, exist_ok=True)

    return input_dir, intermediate_dir, final_output_dir

if __name__ == "__main__":
    setup_project("test_project")