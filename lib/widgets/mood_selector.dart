import 'package:flutter/material.dart';

class MoodSelector extends StatefulWidget {

  final String currentMood;
  final Function(String) onMoodChange;

  const MoodSelector({
    super.key,
    required this.currentMood,
    required this.onMoodChange,
  });


  @override
  Widget build(BuildContext context) {

    final moods = [
      "Normal",
      "Study",
      "Coding",
      "Creative",
      "Business",
      "Research",
      "Chill",
    ];


    return Wrap(

      spacing: 8,
      runSpacing: 8,

      children: moods.map((mood) {

        final selected =
            mood.toLowerCase() ==
            currentMood.toLowerCase();


        return ChoiceChip(

          label: Text(mood),

          selected: selected,


          onSelected: (_) {
            onMoodChange(mood);
          },


          selectedColor: Colors.blue,

          labelStyle: TextStyle(
            color: selected
                ? Colors.white
                : Colors.black,
          ),

        );

      }).toList(),
    );
  }
}