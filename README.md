# Overview

{Important! Do not say in this section that this is college assignment. Talk about what you are trying to accomplish as a software engineer to further your learning.}

/_ The development of a simple chat for instant messages is ideal for a quick comprehension of how the Networking works, understanding Networking is fundamental for development of applications that requires immediate communication and responses. _/

{Provide a description the networking program that you wrote. Describe how to use your software. If you did Client/Server, then you will need to describe how to start both.}

/_ This is a simple chat with a simple GUI that looks to send and receive instant messages from whatever individual using a different server around the world. Following the Client/Server model the individual connects to a main server, and create a quick user without using of a registration site, after this the client can start using the application sending messages and receiving also. The App is not using any type of database so the server keeps track of all messages using own server memory, after finishing a session by restaring the server these messages fade away. _/

{Describe your purpose for writing this software.}

/_ Demonstrate the learning about Networking and how the two or more server interact each other making use of the TCP or UDP models for communication. _/

{Provide a link to your YouTube demonstration. It should be a 4-5 minute demo of the software running (you will need to show two pieces of software running and communicating with each other) and a walkthrough of the code.}

[Software Demo Video](https://youtu.be/zdF2Y_lIbrk)
[GitHub Link](https://github.com/nessnetzld/let-s_chat)
[Deployment Link](https://let-s-chat-son7.onrender.com)

# Network Communication

{Describe the architecture that you used (client/server or peer-to-peer)}

/_ The module used in this project was client-server _/

{Identify if you are using TCP or UDP and what port numbers are used.}

/_ The protocol used is TCP but in an indirect way using HTTP, using the Port: 0.0.0.0:8000 (all network interfaces) _/

{Identify the format of messages being sent between the client and server or the messages sent between two peers.}

/_ Messages are sent to JSON format over HTTP that runs with TCP. _/

# Development Environment

{Describe the tools that you used to develop the software}

/_ Tools utilized during the development of this project was VS Code as the main development environment, with web browser for testing the chat interface and validating client-server. I made used of the terminal to run the Python server and client scripts, and finally Git/GitHub for verson control for tracking changes. _/

{Describe the programming language that you used and any libraries.}

/_ This project was built primarily with Python for the Backend, and JavaScript, HTML, and CSS for the frontend. _/

# Useful Websites

{Make a list of websites that you found helpful in this project}

- [Web Site Name](https://docs.python.org/3/library/socket.html)
- [Web Site Name](https://docs.python.org/3/library/socketserver.html)

# Future Work

{Make a list of things that you need to fix, improve, and add in the future.}

- Item 1
  // Implement a Database model to work with permanent chat history and users.
- Item 2
  // Keep working with the frontend to have an attractive interface for the client and an easy usage environment.
- Item 3
  // Work with a the security of of chats, end-to-end chat encryption to have a save web app.
