<!DOCTYPE html>
<html>

<head>
    <title>Arcade Examples</title>
</head>

<body>
    <ul>
        % for item in examples:
        <li><a href="/example/{{item}}">{{item}}</a></li>
        % end
    </ul>
</body>

</html>