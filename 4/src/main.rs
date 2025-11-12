use std::fs;
use std::io::prelude::*;
use std::net::TcpListener;
use std::net::TcpStream;

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream);
    }
}

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();
    
    let request = String::from_utf8_lossy(&buffer[..]);
    let request_line = request.lines().next().unwrap_or("");
    
    println!("{}", request_line);
    
    // Route handling
    let (status_line, filename) = if request_line.starts_with("GET / HTTP") {
        ("HTTP/1.1 200 OK", "public/index.html")
    } else if request_line.contains("GET /about.html") {
        ("HTTP/1.1 200 OK", "public/about.html")
    } else {
        ("HTTP/1.1 404 NOT FOUND", "public/index.html")
    };

    let contents = fs::read_to_string(filename).unwrap_or_else(|_| {
        String::from("<h1>Error loading page</h1>")
    });

    let response = format!(
        "{}\r\nContent-Length: {}\r\n\r\n{}",
        status_line,
        contents.len(),
        contents
    );

    stream.write_all(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}
