import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import 'typing_animation.dart';


class ChatArea extends StatefulWidget {

  final List<ChatMessage> messages;
  final bool isTyping;


  const ChatArea({
    super.key,
    required this.messages,
    required this.isTyping,
  });


  @override
  State<ChatArea> createState() => _ChatAreaState();

}



class _ChatAreaState extends State<ChatArea> {

  final ScrollController _scrollController = ScrollController();



  @override
  void didUpdateWidget(covariant ChatArea oldWidget) {
    super.didUpdateWidget(oldWidget);


    if (widget.messages.length != oldWidget.messages.length ||
        widget.isTyping != oldWidget.isTyping) {

      Future.delayed(
        const Duration(milliseconds: 100),
        scrollToBottom,
      );

    }

  }



  void scrollToBottom() {

    if (_scrollController.hasClients) {

      _scrollController.animateTo(

        _scrollController.position.maxScrollExtent,

        duration: const Duration(milliseconds: 300),

        curve: Curves.easeOut,

      );

    }

  }



  @override
  Widget build(BuildContext context) {


    if (widget.messages.isEmpty) {

      return const Center(

        child: Column(

          mainAxisAlignment: MainAxisAlignment.center,

          children: [


            Icon(
              Icons.smart_toy,
              size: 120,
            ),


            SizedBox(height: 20),


            Text(
              "Cognit AI",
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),


            Text(
              "Your AI Companion",
            ),


          ],

        ),

      );

    }



    return ListView.builder(

      controller: _scrollController,

      padding: const EdgeInsets.all(16),


      itemCount: widget.messages.length +
          (widget.isTyping ? 1 : 0),



      itemBuilder: (context,index) {



        // typing animation bubble

        if (widget.isTyping &&
            index == widget.messages.length) {


          return const Align(

            alignment: Alignment.centerLeft,


            child: TypingAnimation(),

          );

        }



        final message = widget.messages[index];



        return Align(

          alignment: message.isUser
              ? Alignment.centerRight
              : Alignment.centerLeft,


          child: Container(

            margin: const EdgeInsets.symmetric(
              vertical: 6,
            ),


            padding: const EdgeInsets.all(12),



            decoration: BoxDecoration(

              color: message.isUser
                  ? Colors.blue
                  : Colors.grey.shade800,


              borderRadius:
                  BorderRadius.circular(15),

            ),



            child: Text(

              message.text,

              style: const TextStyle(
                color: Colors.white,
              ),

            ),

          ),

        );

      },

    );

  }



  @override
  void dispose() {

    _scrollController.dispose();

    super.dispose();

  }

}