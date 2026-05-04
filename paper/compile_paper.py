import os
import glob

def compile_manuscript():
    """Compiles all markdown sections into a single manuscript."""
    section_files = sorted(glob.glob("*.md"))
    
    # Filter out the compiled manuscript if it already exists
    section_files = [f for f in section_files if f != "compiled_manuscript.md"]
    
    if not section_files:
        print("No markdown files found to compile.")
        return
        
    print("Found sections to compile:")
    for f in section_files:
        print(f"  - {f}")
        
    compiled_content = ""
    for file in section_files:
        with open(file, 'r', encoding='utf-8') as f:
            compiled_content += f.read() + "\n\n---\n\n"
            
    output_file = "compiled_manuscript.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(compiled_content)
        
    print(f"\n✅ Successfully compiled {len(section_files)} sections into {output_file}!")
    
    # Generate LaTeX
    compile_latex(output_file)

def compile_latex(markdown_file):
    """Converts the compiled markdown into a beautiful LaTeX manuscript using Pandoc."""
    import subprocess
    output_tex = markdown_file.replace(".md", ".tex")
    
    # Using pandoc to generate a standalone LaTeX file
    cmd = [
        "pandoc",
        markdown_file,
        "-o", output_tex,
        "-s",  # standalone document
        "--dpi=300", # High quality images
        "-V", "geometry:margin=1in", # Standard academic margins
        "-V", "fontsize=11pt",
        "-V", "linestretch=1.2", # Better readability
    ]
    
    try:
        print(f"\n🔄 Generating LaTeX version: {output_tex}...")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Successfully compiled LaTeX to {output_tex}!")
    except FileNotFoundError:
        print("⚠️  Pandoc not found. Please install Pandoc to generate LaTeX/PDF.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate LaTeX. Error:\n{e.stderr.decode()}")
    except Exception as e:
        print(f"❌ An error occurred during LaTeX generation: {e}")

if __name__ == "__main__":
    compile_manuscript()
