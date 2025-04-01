import Foundation

class GreifarmClient {
    let serverIP: String
    let port: Int
    
    init(serverIP: String, port: Int = 8005) {
        self.serverIP = serverIP
        self.port = port
    }
    
    // Prüft die Serververbindung
    func checkServerConnection(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "http://\(serverIP):\(port)/") else {
            print("Ungültige URL")
            completion(false)
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { _, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    print("Verbindungsfehler: \(error.localizedDescription)")
                }
                completion(false)
            } else if let httpResponse = response as? HTTPURLResponse {
                DispatchQueue.main.async {
                    if httpResponse.statusCode == 200 {
                        print("Verbindung zum Server erfolgreich (Statuscode: \(httpResponse.statusCode)).")
                    } else {
                        print("Fehlerhafte Antwort vom Server (Statuscode: \(httpResponse.statusCode)).")
                    }
                }
                completion(httpResponse.statusCode == 200)
            }
        }
        task.resume()
    }
    
    func sendServoPositions(x: Int = 90, y: Int = 90, z: Int = 90, completion: @escaping (String) -> Void) {
        checkServerConnection { isConnected in
            if !isConnected {
                completion("Verbindung zum Server konnte nicht hergestellt werden.")
                return
            }
            
            let clampedX = max(90, min(270, x))
            let clampedY = max(90, min(270, y))
            let clampedZ = max(90, min(270, z))
            let data: [String: Any] = ["x": clampedX, "y": clampedY, "z": clampedZ]
            self.sendRequest(data: data, completion: completion)
        }
    }
    
    func toggleMagnet(state: Bool, completion: @escaping (String) -> Void) {
        checkServerConnection { isConnected in
            if !isConnected {
                completion("Verbindung zum Server konnte nicht hergestellt werden.")
                return
            }
            
            let data: [String: Any] = ["magnet": state]
            self.sendRequest(data: data, completion: completion)
        }
    }
    
    func shutdownServer(completion: @escaping (String) -> Void) {
        checkServerConnection { isConnected in
            if !isConnected {
                completion("Verbindung zum Server konnte nicht hergestellt werden.")
                return
            }
            
            let data: [String: Any] = ["shutdown": true]
            self.sendRequest(data: data, completion: completion)
        }
    }
    
    private func sendRequest(data: [String: Any], completion: @escaping (String) -> Void) {
        guard let url = URL(string: "http://\(serverIP):\(port)/") else {
            DispatchQueue.main.async {
                print("Ungültige URL")
                completion("Ungültige URL")
            }
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: data, options: [])
        } catch {
            DispatchQueue.main.async {
                print("JSON-Fehler: \(error.localizedDescription)")
                completion("JSON-Fehler: \(error.localizedDescription)")
            }
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    print("Netzwerkfehler: \(error.localizedDescription)")
                    completion("Netzwerkfehler: \(error.localizedDescription)")
                }
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                DispatchQueue.main.async {
                    print("HTTP-Statuscode: \(httpResponse.statusCode)")
                    if httpResponse.statusCode != 200 {
                        print("Fehlerhafte Antwort vom Server: Statuscode \(httpResponse.statusCode).")
                    }
                }
            }
            
            if let data = data, let responseString = String(data: data, encoding: .utf8) {
                DispatchQueue.main.async {
                    print("Antwort: \(responseString)")
                    completion(responseString)
                }
            } else {
                DispatchQueue.main.async {
                    print("Unerwartete Antwort")
                    completion("Unerwartete Antwort")
                }
            }
        }
        task.resume()
    }
}

// Beispielnutzung
let client = GreifarmClient(serverIP: "192.168.178.151") // IP anpassen
client.sendServoPositions(x: 120, y: 150, z: 200) { response in
    print("Antwort: \(response)")
}
client.toggleMagnet(state: true) { response in
    print("Magnet: \(response)")
}
client.shutdownServer { response in
    print("Shutdown: \(response)")
}
