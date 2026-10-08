<!DOCTYPE html>
<html>

<head>
    <title>Arcade Examples</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .local-link {
            background-color: #4caf50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 20px;
        }
        .local-link:hover {
            background-color: #45a049;
        }
    </style>
</head>

<body>
    <h1>Arcade Examples</h1>
    <a href="/local" class="local-link">🧪 Test Local Scripts</a>
    <h2>Built-in Examples:</h2>
    <ul>
        % for item in examples:
        <li><a href="/example/{{item}}">{{item}}</a></li>
        % end
    </ul>
</body>

</html>