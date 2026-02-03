import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/pictures/popups/defaultImagePopup.dart';

class FavouriteImageRequest extends StatefulWidget {
  final String pictureId;

  const FavouriteImageRequest({Key? key, required this.pictureId})
    : super(key: key);

  @override
  State<FavouriteImageRequest> createState() => _FavouriteImageRequestState();
}

class _FavouriteImageRequestState extends State<FavouriteImageRequest> {
  final FlutterSecureStorage storage = const FlutterSecureStorage();

  List<Map<String, dynamic>> pictures = [];
  String? error;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _fetchPictures();
  }

  Future<void> _fetchPictures() async {
    try {
      final token = await storage.read(key: 'token');

      if (token == null) {
        setState(() {
          error = 'Token is missing';
          loading = false;
        });
        return;
      }

      final pictureResponse = await http.get(
        Uri.parse('$server/get/favourite_images/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (pictureResponse.statusCode != 200) {
        throw Exception('Failed to fetch pictures');
      }

      final pictureData = jsonDecode(pictureResponse.body);

      if (pictureData['data'] == null) {
        setState(() {
          error = 'No pictures found';
          loading = false;
        });
        return;
      }

      List<Map<String, dynamic>> picturesWithThumbnails = [];

      for (var picture in pictureData['data']) {
        final thumbnailResponse = await http.get(
          Uri.parse('$server/get/thumbnail/${picture['picture_serial']}'),
          headers: {'Authorization': token},
        );

        if (thumbnailResponse.statusCode != 200) {
          throw Exception('Failed to fetch thumbnail');
        }

        picturesWithThumbnails.add({
          ...Map<String, dynamic>.from(picture),
          'thumbnailBytes': thumbnailResponse.bodyBytes,
        });
      }

      setState(() {
        pictures = picturesWithThumbnails;
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  void _showPopup(BuildContext context, int index) {
    showDialog(
      context: context,
      builder: (_) => DefaultImagePopup(
        image: pictures[index],
        closePopup: () => Navigator.of(context).pop(),
        onNext: () {
          if (index < pictures.length - 1) {
            Navigator.of(context).pop();
            _showPopup(context, index + 1);
          }
        },
        onPrevious: () {
          if (index > 0) {
            Navigator.of(context).pop();
            _showPopup(context, index - 1);
          }
        },
        hasNext: index < pictures.length - 1,
        hasPrevious: index > 0,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pictures')),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error != null
          ? Center(child: Text(error!))
          : Padding(
              padding: const EdgeInsets.all(8.0),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                ),
                itemCount: pictures.length,
                itemBuilder: (context, index) {
                  final picture = pictures[index];

                  return GestureDetector(
                    onTap: () => _showPopup(context, index),
                    child: Card(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.memory(
                          picture['thumbnailBytes'],
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
    );
  }
}
