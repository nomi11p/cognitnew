import 'package:flutter/material.dart';

class SuggestionChips extends StatelessWidget {
  final Function(String) onSuggestionTap;

  const SuggestionChips({
    super.key,
    required this.onSuggestionTap,
  });

  @override
  Widget build(BuildContext context) {
    final suggestions = [
      "Explain AI",
      "Write Code",
      "Solve Math",
      "Homework",
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: suggestions.map((text) {
        return ActionChip(
          label: Text(text),
          onPressed: () {
            onSuggestionTap(text);
          },
        );
      }).toList(),
    );
  }
}