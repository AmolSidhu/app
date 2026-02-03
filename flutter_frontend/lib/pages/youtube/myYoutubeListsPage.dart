import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/youtube/requests/playlistsRequest.dart';

class MyYoutubeListsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('My YouTube Lists')),
      body: Center(child: YoutubePlaylistsRequest()),
    );
  }
}
