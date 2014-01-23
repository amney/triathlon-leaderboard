<!DOCTYPE html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Greenpark Triathlon 2012</title>
    <?php include("./include/head.php"); ?>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
        google.load("visualization", "1", {packages:["corechart"]});
        google.setOnLoadCallback(drawChart);
        function drawChart() {
            var data = new google.visualization.arrayToDataTable([['Event', '2013 So Far', '2012'], ['Total Competitors', 252, 306], ['Sprint Individual', 117, 76], ['Funathon Individual', 28, 39], ['Sprint Relay', 29, 44], ['Funathon Relay', 9, 22]]);

            var options = {
                title: 'Sign-up Progress'
            };

            var chart = new google.visualization.BarChart(document.getElementById('chart_div'));

            chart.draw(data, options);
        }
    </script>
    <script type='text/javascript'>
        google.load('visualization', '1', {packages:['gauge']});
        google.setOnLoadCallback(drawChart);
        function drawChart() {
            var data = google.visualization.arrayToDataTable([['Label', 'Value'], ['Total Raised', 515]]);

            var options = {
                width: 300, height: 300,
                redFrom: 40000, redTo: 50000,
                yellowFrom:30000, yellowTo: 40000,
                minorTicks: 5, max: 50000,
                majorTicks: ['£0','£25,000','£50,000']
            };

            var chart = new google.visualization.Gauge(document.getElementById('chart_div_0'));

            var formatter = new google.visualization.NumberFormat(
                    {prefix: '£'});
            formatter.format(data, 1);

            chart.draw(data, options);
        }
    </script>
</head>

<body>
<div class="container_12" style="position: relative; top: 0px; padding-top: 20px;">
    <?php include("./include/title.php"); ?>

    <div class="grid_12">
        <div style="margin: auto auto; width: 90%">
            <div id="chart_div_0" style="width: 300px; margin: 0 auto"></div>
            <div id="chart_div" style="height:400px"></div>
        </div>
    </div>

    <?php include("./include/footer.php"); ?>
</div>
</body>
</html>