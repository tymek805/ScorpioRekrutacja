function showData() {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const separator = "##########READING##########\n";
            const data = xhr.responseText.split(separator);
            let table_data = "";
            let x = [0];
            for (let i = 1; i < data.length; i++){
                const reading = data[i].split("\n");
                table_data += "<tr>"; // Już tutaj potrzebuję znać długość
                for (let j = 0; j < reading.length - 1; j++){
                    let type = reading[j].split(" ");
                    if (i === 1) x[j] = type.length;
                    for (let h = 0; h < type.length; h++)
                        table_data += "<td>" + type[h] + "</td>";
                }
                table_data += "</tr>"
            }
            document.getElementById("widget").innerHTML = "<table style='width: 100%'>" + headers(x) + table_data + "</table>";
        }
    };
    xhr.open("GET", "system_data_readings.txt", true);
    xhr.send();
}

function headers(size) {
    let header = "<tr>";
    let subheader = "<tr>";
    let interface_subheader = "<tr>";

    const header_text = ["LOAD [%]", "TEMPERATURE [&degC]", "RAM INFO [BYTES]", "DISK INFO [BYTES]" , "INTERFACE INFO", "NETWORK TRAFFIC [b/s]"]
    for (let i = 0; i < size.length; i++){
        header += "<th colspan='" + size[i] + "'>" + header_text[i] + "</th>";
        for (let j = 0; j < size[i]; j++){
            if (i < 4){
                subheader += "<th rowspan='2'>"
                if (i === 0 || i === 1)
                    subheader += "CORE " + j;
                else if (i === 2){
                    if (j === 0)
                        subheader += "TOTAL";
                    else if (j === 1)
                        subheader += "FREE"
                    else if (j === 2)
                        subheader += "USED"
                }
                else if (i === 3)
                    subheader += "FREE"
            }
            else if (j < size[i] / 2) {
                subheader += "<th colspan='2'>INTERFACE " + j;
                if (i === 4)
                    interface_subheader += "<th> IP ADDRESS </th><th> STATUS </th>"
                else if (i === 5)
                    interface_subheader += "<th> RECEIVED </th><th> SENT </th>"
            }

            subheader += "</th>";
        }
    }
    interface_subheader += "</tr>";
    subheader += "</tr>";
    header += "</tr>";
    return header + subheader + interface_subheader;
}