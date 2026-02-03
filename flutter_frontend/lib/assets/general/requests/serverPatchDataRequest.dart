import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class ServerDataRequestPage extends StatefulWidget {
  const ServerDataRequestPage({super.key});

  @override
  State<ServerDataRequestPage> createState() => _ServerDataRequestPageState();
}

class _ServerDataRequestPageState extends State<ServerDataRequestPage> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Map<String, List<dynamic>> patchData = {};
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    fetchServerData();
  }

  Future<void> fetchServerData() async {
    try {
      final token = await _storage.read(key: 'token');
      if (token == null) {
        setState(() {
          error = 'Authentication token missing.';
          loading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$server/get/server/patch_data/'),
        headers: {'Authorization': token},
      );

      final decoded = json.decode(response.body);

      if (response.statusCode == 200) {
        setState(() {
          patchData = Map<String, List<dynamic>>.from(decoded['data'] ?? {});
        });
      } else {
        setState(() {
          error = decoded['message'] ?? 'Failed to fetch patch notes.';
        });
      }
    } catch (e) {
      debugPrint('Error fetching patch data: $e');
      setState(() {
        error = 'Internal error. Please try again later.';
      });
    } finally {
      setState(() {
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(
        body: Center(child: Text('Loading patch notes...')),
      );
    }

    if (error != null) {
      return Scaffold(
        body: Center(
          child: Text(
            'Error: $error',
            style: const TextStyle(color: Colors.red),
          ),
        ),
      );
    }

    final sortedEntries = patchData.entries.toList()
      ..sort((a, b) => DateTime.parse(b.key).compareTo(DateTime.parse(a.key)));

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 700),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(10),
              boxShadow: const [
                BoxShadow(blurRadius: 12, color: Colors.black12),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Server Patch Updates',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                if (sortedEntries.isEmpty)
                  const Text('No patch notes available.')
                else
                  ...sortedEntries.asMap().entries.map((entry) {
                    final index = entry.key;
                    final date = entry.value.key;
                    final updates = entry.value.value;

                    return Container(
                      margin: const EdgeInsets.only(bottom: 24),
                      padding: const EdgeInsets.only(bottom: 16),
                      decoration: const BoxDecoration(
                        border: Border(
                          bottom: BorderSide(color: Colors.black12),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Update ${sortedEntries.length - index} — $date',
                            style: const TextStyle(
                              color: Colors.blue,
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          ...updates.map<Widget>(
                            (item) => Padding(
                              padding: const EdgeInsets.only(
                                left: 16,
                                bottom: 6,
                              ),
                              child: Text(
                                '• $item',
                                style: const TextStyle(height: 1.6),
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
