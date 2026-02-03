import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/music/requests/customMusicPlaylistRequest.dart';

class CustomMusicPlaylistPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Custom Music Playlist Page')),
      body: Center(child: CustomMusicPlaylistRequest()),
    );
  }
}
