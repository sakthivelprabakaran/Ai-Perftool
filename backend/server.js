const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

app.post('/api/analyze', (req, res) => {
    const { url, format } = req.body;

    if (!url || !format) {
        return res.status(400).json({ error: 'URL and format are required.' });
    }

    // In a real app, sanitize inputs to prevent command injection.
    const sanitizedFormat = format === 'jmeter' ? 'jmeter' : 'loadrunner';

    // The python script's project root is the parent of the backend directory
    const projectRoot = path.join(__dirname, '..');

    // Command to execute the python script
    const command = `PYTHONPATH=${path.join(projectRoot, 'ai-engine')} python3 -m ai_engine.main --format ${sanitizedFormat}`;

    console.log(`Executing command: ${command} in directory ${projectRoot}`);

    exec(command, { cwd: projectRoot }, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).json({ error: 'Failed to execute analysis script.', details: stderr });
        }

        console.log(`stdout: ${stdout}`);

        // Parse stdout to find the path of the generated file/directory
        const jmeterMatch = stdout.match(/JMeter test plan has been saved to: (.*)/);
        const loadrunnerMatch = stdout.match(/LoadRunner script '.*' created at (.*)/);

        const filePath = jmeterMatch ? jmeterMatch[1].trim() : (loadrunnerMatch ? loadrunnerMatch[1].trim() : null);

        if (!filePath) {
             return res.status(500).json({ error: 'Could not determine output file path from script.', details: stdout });
        }

        res.json({ message: 'Analysis complete!', outputFile: filePath });
    });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
