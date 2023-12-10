// import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

// // Use the global variable `rawEmotions`
// console.log(emotions); // To check if the data is available

// // const emotions = [
// //     { date: '2000-01-01', emotion: 'Emotion1', intensity: 10 },
// //     { date: '2000-01-01', emotion: 'Emotion2', intensity: 15 },
// //     { date: '2000-01-01', emotion: 'Emotion3', intensity: 20 },
// //     { date: '2000-02-01', emotion: 'Emotion1', intensity: 20 },
// //     { date: '2000-02-01', emotion: 'Emotion2', intensity: 10 },
// //     { date: '2000-02-01', emotion: 'Emotion3', intensity: 40 },
// //     // ... more data
// //   ];

// function stackedChart(){
//     // Specify the chart’s dimensions.
//     const width = 928;
//     const height = 500;
//     const marginTop = 20;
//     const marginRight = 20;
//     const marginBottom = 20;
//     const marginLeft = 40;


//     // Convert string dates to Date objects for D3
//     emotions.forEach(d => {
//         d.date = new Date(d.date);
//     });

//     // Get unique emotion keys
//     const emotionKeys = Array.from(new Set(emotions.flatMap(d => Object.keys(d).filter(k => k !== 'date'))));

//     // Stack the data
//     const series = d3.stack()
//         .keys(emotionKeys)
//         .offset(d3.stackOffsetExpand)(emotions);

//     // Prepare the scales for positional and color encodings.
//     const x = d3.scaleUtc()
//         .domain(d3.extent(emotions, d => d.date))
//         .range([marginLeft, width - marginRight]);

//     const y = d3.scaleLinear()
//         .rangeRound([height - marginBottom, marginTop]);

//     const color = d3.scaleOrdinal()
//         .domain(series.map(d => d.key))
//         .range(d3.schemeTableau10);

//     // Construct an area shape.
//     const area = d3.area()
//         .x(d => x(d.data.date)) // Corrected x-accessor
//         .y0(d => y(d[0]))
//         .y1(d => y(d[1]));

//     // Create the SVG container.
//     const svg = d3.create("svg")
//         .attr("width", width)
//         .attr("height", height)
//         .attr("viewBox", [0, 0, width, height])
//         .attr("style", "max-width: 100%; height: auto;");

//     // Append a path for each series.
//     svg.append("g")
//         .selectAll()
//         .data(series)
//         .join("path")
//         .attr("fill", d => color(d.key))
//         .attr("d", area)
//         .append("title")
//         .text(d => d.key);

//     // Append the x axis, and remove the domain line.
//     svg.append("g")
//         .attr("transform", `translate(0,${height - marginBottom})`)
//         .call(d3.axisBottom(x).tickSizeOuter(0))
//         .call(g => g.select(".domain").remove());

//     // Add the y axis, remove the domain line, add grid lines and a label.
//     svg.append("g")
//         .attr("transform", `translate(${marginLeft},0)`)
//         .call(d3.axisLeft(y).ticks(height / 80, "%"))
//         .call(g => g.select(".domain").remove())
//         .call(g => g.selectAll(".tick line")
//             .filter(d => d === 0 || d === 1)
//             .clone()
//             .attr("x2", width - marginLeft - marginRight))
//         .call(g => g.append("text")
//             .attr("x", -marginLeft)
//             .attr("y", 10)
//             .attr("fill", "currentColor")
//             .attr("text-anchor", "start")
//             .text("Emotions breakdown"));

//     // // Return the chart with the color scale as a property (for the legend).
//     // return Object.assign(svg.node(), {scales: {color}});

//     // Return the SVG node
//     return svg.node();
// }

// // Select the container where the chart should be added and call the function
// d3.select('#chart-container').append(() => stackedChart());
