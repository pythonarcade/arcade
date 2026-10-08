<!DOCTYPE html>
<html>

<head>
    <title>Local Scripts</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        h1 {
            color: #333;
        }
        .info {
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 10px 0;
        }
        a {
            color: #0066cc;
            text-decoration: none;
            font-size: 16px;
        }
        a:hover {
            text-decoration: underline;
        }
        .back-link {
            margin-top: 30px;
            display: block;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>

<body>
    <h1>Local Test Scripts</h1>

    <div class="info">
        <p><strong>How to use:</strong></p>
        <p>Place your Python scripts in the <code>webplayground/local_scripts/</code> directory.</p>
        <p>Scripts should have a <code>main()</code> function that will be called when loaded.</p>
        <p>No need to restart the server - just refresh this page to see new scripts!</p>
    </div>

    % if scripts:
    <h2>Available Scripts:</h2>
    <ul>
        % for script in scripts:
        <li><a href="/local/{{script}}">{{script}}</a></li>
        % end
    </ul>
    % else:
    <p>No local scripts found. Add .py files to the <code>local_scripts/</code> directory.</p>
    % end

    <a href="/" class="back-link">← Back to Examples</a>
</body>

</html>

