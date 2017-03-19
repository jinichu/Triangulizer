const express = require('express');
const fileUpload = require('express-fileupload');
const app = express();
app.use(express.static('src/public'));
app.use(fileUpload());
app.post('/', function (req, res) {
    if (!req.files)
        return res.status(400).send('No files were uploaded.');
    console.log(req.files);
    const sampleFile = req.files.sampleFile;
    sampleFile.mv('/somewhere/on/your/server/filename.pdf', function (err) {
        if (err) {
            return res.status(500).send(err);
        }
        res.send('File uploaded!');
    });
});
app.listen(3000, function () {
    console.log('Listening on port 3000!');
});
