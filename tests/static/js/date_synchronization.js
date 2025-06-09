document.addEventListener('DOMContentLoaded', () => {
    const dateIn = document.getElementById('id_date_in');
    const dateOut = document.getElementById('id_date_out');
    const form = document.getElementById('testForm');


    dateIn.addEventListener('change', (e) => {
        console.log(e.target.value);
        const minData = new Date(dateIn.min)
        const dateInData = new Date(dateIn.value);

        if (minData.getDate() === dateInData.getDate()) {
            const minTime = minData.getHours() * 60 + minData.getMinutes();
            const fieldTime = dateInData.getHours() * 60 + dateInData.getMinutes();

            if (minTime > fieldTime) {
                dateIn.value = dateIn.min
            }

        };
        
        if (dateOut.value < dateIn.value) {
            const newDateIn = new Date(dateIn.value)
            newDateIn.setHours(newDateIn.getHours() + 4)
            dateOut.value = newDateIn.toISOString().slice(0, 16);
        }

        dateOut.min = e.target.value;
    });


    dateOut.addEventListener('change', (e) => {
        console.log(e.target.value);
        const minData = new Date(dateOut.min)
        const dateOutData = new Date(dateOut.value);

        if (minData.getDate() === dateOutData.getDate()) {
            const minTime = minData.getHours() * 60 + minData.getMinutes();
            const fieldTime = dateOutData.getHours() * 60 + dateOutData.getMinutes();
            
            console.log(minData.toISOString())
            minData.setHours(minData.getHours() + 4)
            console.log(minData.toISOString());
            if (minTime > fieldTime) {
                dateOut.value = minData.toISOString().slice(0, 16)
            }
        };
    });
})