import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://192.168.1.4:8080";

static Future<String> sendMessage(
  String message,
  String mood,
) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/chat"),
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "prompt": message,
          "mood": mood,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        return data["response"] ?? "No response";
      }

      return "Server Error: ${response.statusCode}";

    } catch (e) {
      return "Unable to connect to Cognit.";
    }
  }
}