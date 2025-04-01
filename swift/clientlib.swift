import Foundation

class GreifarmClient {
    let serverIP: String
    let port: Int
    
    init(serverIP: String, port: Int = 8005) {
        self.serverIP = serverIP
        self.port = port
    }
    
    func sendServoPositions(x: Int = 90, y: Int = 90, z: Int = 90, completion: @escaping (String) -> Void) {
        let clampedX = max(90, min(270, x))
        let clampedY = max(90, min(270, y))
        let clampedZ = max(90, min(270, z))
        let data: [String: Any] = ["x": clampedX, "y": clampedY, "z": clampedZ]
        sendRequest(data: data, completion: completion)
    }
    
    func toggleMagnet(state: Bool, completion: @escaping (String) -> Void) {
        let data: [String: Any] = ["magnet": state]
        sendRequest(data: data, completion: completion)
    }
    
    func shutdownServer(completion: @escaping (String) -> Void) {
        let data: [String: Any] = ["shutdown": true]
        sendRequest(data: data, completion: completion)
    }
    
    private func sendRequest(data: [String: Any], completion: @escaping (String) -> Void) {
        guard let url = URL(string: "http://\(serverIP):\(port)/") else {
            completion("Ungültige URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: data, options: [])
        } catch {
            completion("JSON-Fehler: \(error.localizedDescription)")
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion("Netzwerkfehler: \(error.localizedDescription)")
                return
            }
            
            if let data = data, let responseString = String(data: data, encoding: .utf8) {
                completion(responseString)
            } else {
                completion("Unerwartete Antwort")
            }
        }
        task.resume()
    }
}

// Beispielnutzung
let client = GreifarmClient(serverIP: "192.168.1.100") // IP anpassen
client.sendServoPositions(x: 120, y: 150, z: 200) { response in
    print("Antwort: \(response)")
}
client.toggleMagnet(state: true) { response in
    print("Magnet: \(response)")
}
client.shutdownServer { response in
    print("Shutdown: \(response)")
}
