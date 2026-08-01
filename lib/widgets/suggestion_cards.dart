import 'package:flutter/material.dart';

class SuggestionCards extends StatelessWidget {
  const SuggestionCards({super.key});

  @override
  Widget build(BuildContext context) {
    final suggestions = [
      "✍️ Write a paragraph",
      "📚 Explain a topic",
      "💻 Help me code",
      "💡 Brainstorm ideas",
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        alignment: WrapAlignment.center,
        children: suggestions.map((text) {
          return Container(
            width: 160,
            height: 55,
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: Colors.white12,
              ),
            ),
            child: Center(
              child: Text(
                text,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 14,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}