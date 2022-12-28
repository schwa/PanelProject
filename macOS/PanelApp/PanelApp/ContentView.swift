//
//  ContentView.swift
//  PanelApp
//
//  Created by Jonathan Wight on 12/27/22.
//

import SwiftUI

class Model: ObservableObject {
    func main() {
        let task = URLSession.shared.webSocketTask(with: URL(string: "ws://localhost:8765")!)
        print(task)
        // Connect, handles handshake
        task.resume()
        // Send “Hello!” to the server
        print("Sending")
        let textMessage = URLSessionWebSocketTask.Message.string("Hello!")
        task.send(textMessage) { error in
            print(error)
        }
        task.receive { result in
            print(result)
            task.cancel(with: .normalClosure, reason: nil)
        }
    }
}

struct ContentView: View {

    @StateObject
    var model = Model()

    var body: some View {
        VStack {
            Button("Connect?") {
                model.main()
            }
        }
        .padding()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

//mport Foundation
//// Create a websocket with a URL
//let task = URLSession.shared.webSocketTask(with: URL(string: “wss://websocket.example”)!)
//                                                     // Connect, handles handshake
//                                                     task.resume()
//                                                     // Send “Hello!” to the server
//                                                     let textMessage = URLSessionWebSocketTask.Message.string(“Hello!”)
//                                                     task.send(textMessage) { error in /* Handle error */ }
//                                                     // Listen for messages from the server
//                                                     task.receive { result in /* Result type with data/string success responses */ }
//                                                     task.sendPing { error in /* Handle error */ }
//                                                     // Close the socket
//                                                     task.cancel(with: .normalClosure, reason: nil)
