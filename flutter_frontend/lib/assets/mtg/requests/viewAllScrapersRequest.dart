import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/mtg/requests/viewScraperHistoryRequest.dart';

class ViewAllScraperRequest extends StatefulWidget {
  const ViewAllScraperRequest({Key? key}) : super(key: key);

  @override
  State<ViewAllScraperRequest> createState() => _ViewAllScraperRequestState();
}

class _ViewAllScraperRequestState extends State<ViewAllScraperRequest> {
  final _storage = const FlutterSecureStorage();
  List<dynamic> _scrapers = [];
  String? _errorMessage;
  String? _successMessage;
  bool _loading = false;
  bool _triggering = false;

  @override
  void initState() {
    super.initState();
    _fetchScrapers();
  }

  Future<void> _fetchScrapers() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      final response = await http.get(
        Uri.parse('$server/get/all_scraper_statuses/'),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final scrapersMap = data['scrapers'] as Map<String, dynamic>? ?? {};
        setState(() {
          _scrapers = scrapersMap.entries
              .map((e) => {'serial': e.key, ...e.value})
              .toList();
        });
      } else {
        setState(() {
          _errorMessage = 'Failed to fetch scrapers: ${response.reasonPhrase}';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error fetching scrapers: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  Future<void> _runScraper(String serial) async {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
      _triggering = true;
    });

    try {
      final token = await _storage.read(key: 'token');
      final response = await http.post(
        Uri.parse('$server/trigger/mtg_f2f_scraper/$serial/'),
        headers: {'Authorization': token ?? ''},
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        setState(() {
          _successMessage = 'Scraper $serial triggered successfully.';
        });
      } else {
        setState(() {
          _errorMessage = data['error'] ?? 'Failed to trigger scraper.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error triggering scraper: $e';
      });
    } finally {
      setState(() {
        _triggering = false;
      });
    }
  }

  void _viewPreviousSessions(String serial) async {
    try {
      await _storage.write(key: 'scraperSerial', value: serial);

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => const ViewScraperHistoryRequest(),
        ),
      );
    } catch (e) {
      setState(() {
        _errorMessage = 'Error opening scraper history: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('All Scrapers')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_errorMessage != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  if (_successMessage != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        _successMessage!,
                        style: const TextStyle(color: Colors.green),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  Expanded(
                    child: _scrapers.isEmpty
                        ? const Center(child: Text('No scrapers found.'))
                        : ListView.builder(
                            itemCount: _scrapers.length,
                            itemBuilder: (context, index) {
                              final scraper = _scrapers[index];
                              final status = scraper['status'] ?? '';
                              final serial = scraper['serial'] ?? '';
                              final fileName = scraper['file_name'] ?? '';
                              final createDate = scraper['create_date'] ?? '';

                              return Card(
                                margin: const EdgeInsets.symmetric(vertical: 8),
                                child: Padding(
                                  padding: const EdgeInsets.all(12),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        fileName,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text('Status: $status'),
                                      const SizedBox(height: 4),
                                      Text(
                                        'Created: ${DateTime.tryParse(createDate)?.toLocal().toString() ?? createDate}',
                                      ),
                                      const SizedBox(height: 8),
                                      Row(
                                        children: [
                                          ElevatedButton(
                                            onPressed:
                                                status == 'validated' &&
                                                    !_triggering
                                                ? () => _runScraper(serial)
                                                : null,
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor:
                                                  status == 'validated'
                                                  ? Colors.green
                                                  : Colors.grey,
                                            ),
                                            child: _triggering
                                                ? const SizedBox(
                                                    width: 16,
                                                    height: 16,
                                                    child:
                                                        CircularProgressIndicator(
                                                          strokeWidth: 2,
                                                          color: Colors.white,
                                                        ),
                                                  )
                                                : const Text('Run Scraper'),
                                          ),
                                          const SizedBox(width: 8),
                                          TextButton(
                                            onPressed: () =>
                                                _viewPreviousSessions(serial),
                                            style: TextButton.styleFrom(
                                              backgroundColor: Colors.blue,
                                              foregroundColor: Colors.white,
                                            ),
                                            child: const Text(
                                              'View Previous Sessions',
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
      ),
    );
  }
}
