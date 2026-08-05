import 'package:flutter/material.dart';
import 'banner_ad.dart';

class AppDrawer extends StatefulWidget {
  const AppDrawer({super.key});

  @override
  State<AppDrawer> createState() => _AppDrawerState();
}

class _AppDrawerState extends State<AppDrawer> {
  String selectedMood = "Normal";

  final List<String> moods = [
    "Normal",
    "Study",
    "Coding",
    "Creative",
    "Business",
    "Research",
  ];

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [

          const DrawerHeader(
            decoration: BoxDecoration(),

            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,

              children: [

                Icon(
                  Icons.smart_toy,
                  size: 50,
                ),

                SizedBox(height: 10),

                Text(
                  "🧠 Cognit Infinity",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),

              ],
            ),
          ),


          const Padding(
            padding: EdgeInsets.all(12),
            child: Text(
              "WORKSPACE",
              style: TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),


          ListTile(
            leading: Icon(Icons.chat),
            title: Text("Chats"),
            trailing: Text("Coming Soon"),
          ),


          ListTile(
            leading: Icon(Icons.login),
            title: Text("Login"),
            trailing: Text("Coming Soon"),
          ),


          ListTile(
            leading: Icon(Icons.library_books),
            title: Text("Library"),
            trailing: Text("Coming Soon"),
          ),


          ListTile(
            leading: Icon(Icons.mic),
            title: Text("Voice"),
            trailing: Text("Coming Soon"),
          ),


          Divider(),


          const Padding(
            padding: EdgeInsets.all(12),
            child: Text(
              "TOOLS",
              style: TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),


          ListTile(
            leading: Icon(Icons.public),
            title: Text("Browser"),
            trailing: Text("Coming Soon"),
          ),


          ListTile(
            leading: Icon(Icons.science),
            title: Text("Research"),
            trailing: Text("Coming Soon"),
          ),


          ListTile(
            leading: Icon(Icons.code),
            title: Text("Coding"),
            trailing: Text("Coming Soon"),
          ),


          ListTile(
            leading: Icon(Icons.favorite),
            title: Text("Support Cognit"),
          ),


          Divider(),


          const Padding(
            padding: EdgeInsets.all(12),
            child: Text(
              "MOODS",
              style: TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),


          const Padding(
            padding: EdgeInsets.symmetric(vertical: 8),
            child: BannerAdWidget(),
          ),


          ...moods.map((mood) {

            bool active = selectedMood == mood;


            return ListTile(

              title: Text(mood),

              leading: Icon(
                active
                    ? Icons.check_circle
                    : Icons.circle_outlined,
              ),


              selected: active,


              selectedTileColor:
                  Colors.blue.withOpacity(0.2),


              onTap: () {

                setState(() {
                  selectedMood = mood;
                });

              },

            );

          }),

        ],
      ),
    );
  }
}