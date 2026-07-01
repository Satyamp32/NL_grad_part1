import subprocess
import os
import sys

def main():
    print("=== Starting Spotify Growth PM Presentation PDF Compilation ===")
    
    # 1. Resolve absolute paths
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(workspace_dir, "Presentation", "index.html")
    output_pdf = os.path.join(workspace_dir, "NL Spotify.pdf")
    
    html_url = f"file://{html_file}"
    
    print(f"Workspace path: {workspace_dir}")
    print(f"Source HTML: {html_file}")
    print(f"Output PDF: {output_pdf}")
    
    if not os.path.exists(html_file):
        print(f"Error: Source file {html_file} does not exist!")
        sys.exit(1)
        
    # 2. Chrome executable path on macOS
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    if not os.path.exists(chrome_path):
        print(f"Error: Google Chrome executable not found at: {chrome_path}")
        print("Please ensure Google Chrome is installed on this macOS machine.")
        sys.exit(1)
        
    # 3. Construct headless command
    # --print-to-pdf: prints to file
    # --print-to-pdf-no-header: hides native headers/footers (page number, date, URL, etc.)
    # --no-margins: ensures page border matches design CSS perfectly
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={output_pdf}",
        "--print-to-pdf-no-header",
        "--no-margins",
        html_url
    ]
    
    print(f"Executing command: {' '.join(cmd)}")
    
    try:
        # Run process synchronously
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Chrome output (stdout):", result.stdout)
        print("Chrome error (stderr):", result.stderr)
        
        # 4. Check results
        if os.path.exists(output_pdf):
            file_size_kb = os.path.getsize(output_pdf) / 1024.0
            print(f"Success! PDF generated successfully.")
            print(f"Location: {output_pdf}")
            print(f"File Size: {file_size_kb:.2f} KB ({file_size_kb / 1024.0:.2f} MB)")
            
            # Guidelines check (40MB limit)
            if file_size_kb / 1024.0 < 40.0:
                print("Size check: PASSED (Under 40MB limit)")
            else:
                print("Warning: Size check FAILED (Over 40MB limit)")
        else:
            print("Error: Command finished but PDF file was not generated.")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print("Error executing Chrome headless print-to-pdf:")
        print(e.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()
