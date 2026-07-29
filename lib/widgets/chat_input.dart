import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {

  final Function(String) onSend;

  const ChatInput({
    super.key,
    required this.onSend,
  });

  @override
  State<ChatInput> createState() => _ChatInputState();
}


class _ChatInputState extends State<ChatInput> {

  final controller = TextEditingController();


  void sendMessage() {

    if (controller.text.trim().isEmpty) {
      return;
    }

    widget.onSend(controller.text);

    controller.clear();
  }


  @override
  Widget build(BuildContext context) {

    return Padding(
      padding: const EdgeInsets.all(12),

      child: Row(
        children: [

          Expanded(
            child: TextField(
              controller: controller,

              decoration: InputDecoration(
                hintText: "Ask Cognit anything...",
                filled: true,
                fillColor: const Color(0xFF1E293B),

                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(25),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),


          const SizedBox(width: 10),


          CircleAvatar(
            child: IconButton(
              icon: const Icon(Icons.send),
              onPressed: sendMessage,
            ),
          )

        ],
      ),
    );
  }
}