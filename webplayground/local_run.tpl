<!DOCTYPE html>
<html>

<head>
    <title>{{script_name}}</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        #status {
            position: fixed;
            top: 10px;
            right: 10px;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            font-family: Arial, sans-serif;
            z-index: 1000;
        }
        .loading {
            color: #ff9800;
        }
        .ready {
            color: #4caf50;
        }
        .error {
            color: #f44336;
        }
    </style>
</head>

<body>
    <div id="status" class="loading">Loading...</div>
    <script type="text/javascript">
        async function main() {
            const statusDiv = document.getElementById('status');

            try {
                statusDiv.textContent = 'Loading Pyodide...';
                let pyodide = await loadPyodide();

                statusDiv.textContent = 'Installing packages...';
                await pyodide.loadPackage("micropip");
                const micropip = pyodide.pyimport("micropip");
                await pyodide.loadPackage("pillow");
                await micropip.install("http://localhost:8000/static/{{arcade_wheel}}", pre=true);

                statusDiv.textContent = 'Loading script...';

                // Fetch the script content with cache-busting timestamp
                const timestamp = new Date().getTime();
                const response = await fetch("/local_scripts/{{script_name}}.py?t=" + timestamp);
                const scriptContent = await response.text();

                statusDiv.textContent = 'Running script...';
                statusDiv.className = 'ready';

                // Execute the script content (this will run the if __name__ == "__main__" block)
                pyodide.runPython(scriptContent);


                statusDiv.textContent = 'Ready';
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 2000);

            } catch (error) {
                statusDiv.textContent = 'Error: ' + error.message;
                statusDiv.className = 'error';
                console.error(error);
            }
        }
        main();
    </script>
</body>

</html>

