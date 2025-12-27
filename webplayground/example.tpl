<!DOCTYPE html>
<html>

<head>
    % title = name.split(".")[-1]
    <title>{{title}}</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js"></script>
</head>

<body>
    <script type="text/javascript">
        async function main() {
            let pyodide = await loadPyodide();
            await pyodide.loadPackage("micropip");
            const micropip = pyodide.pyimport("micropip");
            await pyodide.loadPackage("pillow");
            await micropip.install("http://localhost:8000/static/{{arcade_wheel}}", pre=true);

            // We are importing like this because some example files have numbers in the name, and you can't use those in normal import statements
            pyodide.runPython(`
                import importlib
                module = importlib.import_module("{{name}}")
                module.main()
            `)
        }
        main();
    </script>
</body>

</html>