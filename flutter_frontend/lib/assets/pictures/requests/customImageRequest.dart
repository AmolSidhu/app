import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/pictures/popups/defaultImagePopup.dart';

class CustomImageRequest extends StatefulWidget {
  final String pictureId;

  const CustomImageRequest({Key? key, required this.pictureId})
    : super(key: key);

  @override
  State<CustomImageRequest> createState() => _CustomImageRequest();
}

class _CustomImageRequest extends State<CustomImageRequest> {
  final storage = const FlutterSecureStorage();
  List<Map<String, dynamic>> pictures = [];
  String? error;

  @override
  void initState() {
    super.initState();
    _fetchPictures();
  }

  Future<void> _fetchPictures() async {
    try {
      final token = await storage.read(key: 'token');
      final albumSerial = await storage.read(key: 'customAlbumSerial');

      if (albumSerial == null) {
        setState(() {
          error = 'Album parameter is missing';
        });
        return;
      }

      final pictureResponse = await http.get(
        Uri.parse('$server/get/custom_album_images/$albumSerial'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (pictureResponse.statusCode != 200) {
        throw Exception('Failed to fetch pictures');
      }

      final pictureData = jsonDecode(pictureResponse.body);

      if (pictureData['data'] != null) {
        List<Map<String, dynamic>> picturesWithThumbnails = [];
        for (var picture in pictureData['data']) {
          final thumbnailResponse = await http.get(
            Uri.parse('$server/get/thumbnail/${picture['picture_serial']}'),
            headers: {
              'Authorization': token ?? '',
              'Content-Type': 'application/json',
            },
          );

          if (thumbnailResponse.statusCode != 200) {
            throw Exception('Failed to fetch thumbnail');
          }

          final imageUrl =
              'data:image/jpeg;base64,${base64Encode(thumbnailResponse.bodyBytes)}';

          picturesWithThumbnails.add({...picture, 'thumbnailUrl': imageUrl});
        }

        setState(() {
          pictures = picturesWithThumbnails;
        });
      } else {
        setState(() {
          error = 'No pictures found';
        });
      }
    } catch (e) {
      setState(() {
        error = e.toString();
      });
    }
  }

  void _showPopup(BuildContext context, Map<String, dynamic> image, int index) {
    showDialog(
      context: context,
      builder: (context) {
        return DefaultImagePopup(
          image: image,
          closePopup: () {
            Navigator.of(context).pop();
          },
          onNext: () {
            Navigator.of(context).pop();
            _showPopup(
              context,
              pictures[(index + 1) % pictures.length],
              index + 1,
            );
          },
          onPrevious: () {
            Navigator.of(context).pop();
            _showPopup(
              context,
              pictures[(index - 1 + pictures.length) % pictures.length],
              index - 1,
            );
          },
          hasNext: index < pictures.length - 1,
          hasPrevious: index > 0,
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Pictures')),
        body: Center(child: Text(error!)),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Pictures')),
      body: pictures.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(8.0),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 8.0,
                  mainAxisSpacing: 8.0,
                  childAspectRatio: 1.0,
                ),
                itemCount: pictures.length,
                itemBuilder: (context, index) {
                  final picture = pictures[index];
                  return GestureDetector(
                    onTap: () => _showPopup(context, picture, index),
                    child: Card(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8.0),
                        child: SizedBox(
                          width: double.infinity,
                          height: double.infinity,
                          child: Image.memory(
                            base64Decode(picture['thumbnailUrl'].split(',')[1]),
                            fit: BoxFit.cover,
                          ),
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
