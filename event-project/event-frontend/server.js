// Import dependencies
const express = require('express');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

// Set up the Express app
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Set up the home route
app.get('/', (req, res) => {
    res.send(`
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                color: #333;
                padding: 20px;
            }
            h1, h2 {
                color: #0066cc;
            }
            form {
                background-color: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 400px;
                margin: 20px auto;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input[type="text"] {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            input[type="submit"] {
                background-color: #0066cc;
                color: #fff;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #005bb5;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background-color: #fff;
                padding: 10px;
                border: 1px solid #ccc;
                margin-bottom: 5px;
                border-radius: 4px;
            }
        </style>
        <h1>Event Management System</h1>
        <form action="/events" method="POST">
            <label for="title">Title:</label><br>
            <input type="text" id="title" name="title"><br>
            <label for="description">Description:</label><br>
            <input type="text" id="description" name="description"><br>
            <label for="date">Date:</label><br>
            <input type="text" id="date" name="date"><br><br>
            <input type="submit" value="Create Event">
        </form>
    `);
});

// Route to handle creating an event
app.post('/events', async (req, res) => {
    const { title, description, date } = req.body;
    
    try {
        const response = await axios.post('http://localhost:8000/events/', {
            title,
            description,
            date
        });
        res.send(`
            <style>
                ${getCommonStyles()}
            </style>
            <h2>Event Created</h2>
            <p>ID: ${response.data.id}</p>
            <p>Title: ${response.data.title}</p>
            <p>Description: ${response.data.description}</p>
            <p>Date: ${response.data.date}</p>
            <a href="/">Back to Home</a>
        `);
    } catch (error) {
        res.status(500).send('Error creating event');
    }
});

// Route to display all events
app.get('/events', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/events/');
        const events = response.data;
        
        let eventsList = '<h2>All Events</h2><ul>';
        events.forEach(event => {
            eventsList += `<li>${event.title} - ${event.date} [<a href="/events/${event.id}">View</a>]</li>`;
        });
        eventsList += '</ul><a href="/">Back to Home</a>';

        res.send(`
            <style>
                ${getCommonStyles()}
            </style>
            ${eventsList}
        `);
    } catch (error) {
        res.status(500).send('Error fetching events');
    }
});

// Route to view a specific event
app.get('/events/:eventId', async (req, res) => {
    const { eventId } = req.params;

    try {
        const response = await axios.get(`http://localhost:8000/events/${eventId}`);
        const event = response.data;

        res.send(`
            <style>
                ${getCommonStyles()}
            </style>
            <h2>Event Details</h2>
            <p>ID: ${event.id}</p>
            <p>Title: ${event.title}</p>
            <p>Description: ${event.description}</p>
            <p>Date: ${event.date}</p>
            <a href="/events/${eventId}/edit">Edit</a> |
            <form action="/events/${eventId}" method="POST" style="display:inline;">
                <input type="hidden" name="_method" value="DELETE">
                <input type="submit" value="Delete" style="background-color: #ff4d4d; color: #fff; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer;">
            </form>
            <a href="/events">Back to Events</a>
        `);
    } catch (error) {
        res.status(500).send('Error fetching event');
    }
});

// Route to handle editing an event
app.get('/events/:eventId/edit', (req, res) => {
    const { eventId } = req.params;

    res.send(`
        <style>
            ${getCommonStyles()}
        </style>
        <h2>Edit Event</h2>
        <form action="/events/${eventId}" method="POST">
            <input type="hidden" name="_method" value="PUT">
            <label for="title">Title:</label><br>
            <input type="text" id="title" name="title"><br>
            <label for="description">Description:</label><br>
            <input type="text" id="description" name="description"><br>
            <label for="date">Date:</label><br>
            <input type="text" id="date" name="date"><br><br>
            <input type="submit" value="Update Event">
        </form>
        <a href="/events">Back to Events</a>
    `);
});

app.post('/events/:eventId', async (req, res) => {
    const { eventId } = req.params;
    const { title, description, date } = req.body;

    try {
        const response = await axios.put(`http://localhost:8000/events/${eventId}`, {
            title,
            description,
            date
        });
        res.send(`
            <style>
                ${getCommonStyles()}
            </style>
            <h2>Event Updated</h2>
            <p>ID: ${response.data.id}</p>
            <p>Title: ${response.data.title}</p>
            <p>Description: ${response.data.description}</p>
            <p>Date: ${response.data.date}</p>
            <a href="/events">Back to Events</a>
        `);
    } catch (error) {
        res.status(500).send('Error updating event');
    }
});

// Route to handle deleting an event
app.delete('/events/:eventId', async (req, res) => {
    const { eventId } = req.params;

    try {
        await axios.delete(`http://localhost:8000/events/${eventId}`);
        res.send(`
            <style>
                ${getCommonStyles()}
            </style>
            <h2>Event Deleted</h2>
            <a href="/events">Back to Events</a>
        `);
    } catch (error) {
        res.status(500).send('Error deleting event');
    }
});

// Function to return common styles
function getCommonStyles() {
    return `
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
            padding: 20px;
        }
        h1, h2 {
            color: #0066cc;
        }
        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 20px auto;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        input[type="submit"] {
            background-color: #0066cc;
            color: #fff;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #005bb5;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background-color: #fff;
            padding: 10px;
            border: 1px solid #ccc;
            margin-bottom: 5px;
            border-radius: 4px;
        }
    `;
}



// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
