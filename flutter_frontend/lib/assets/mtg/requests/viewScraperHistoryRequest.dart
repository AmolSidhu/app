import 'dart:html' as html;
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class ViewScraperHistoryRequest extends StatefulWidget {
  const ViewScraperHistoryRequest({Key? key}) : super(key: key);

  @override
  State<ViewScraperHistoryRequest> createState() =>
      _ViewScraperHistoryRequestState();
}

class _ViewScraperHistoryRequestState extends State<ViewScraperHistoryRequest> {
  final _storage = const FlutterSecureStorage();

  List<dynamic> _history = [];
  bool _loading = false;
  String? _errorMessage;
  String? _successMessage;
  String? _scraperSerial;

  @override
  void initState() {
    super.initState();
    _loadScraperSerialAndFetchHistory();
  }

  Future<void> _loadScraperSerialAndFetchHistory() async {
    final serial = await _storage.read(key: 'scraperSerial');
    if (serial == null || serial.isEmpty) {
      setState(() {
        _errorMessage = 'No scraper serial found in storage.';
      });
      return;
    }
    setState(() => _scraperSerial = serial);
    await _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    if (_scraperSerial == null || _scraperSerial!.isEmpty) return;

    setState(() {
      _loading = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      final url = Uri.parse('$server/get/scraper_status/$_scraperSerial/');

      final response = await http.get(
        url,
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode != 200) {
        setState(() {
          _errorMessage = 'Server returned an error: ${response.body}';
        });
        return;
      }

      final data = jsonDecode(response.body);
      final outputs =
          (data['scraper_outputs'] as Map<String, dynamic>?)?.entries
              .map((e) => {'serial_output': e.key, ...e.value})
              .toList() ??
          [];

      setState(() {
        _history = outputs;
        if (_history.isEmpty) {
          _successMessage = 'No scraper history found for this serial.';
        }
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Error fetching history: $e';
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _downloadFile(String serialOutput) async {
    if (_scraperSerial == null) return;

    try {
      final token = await _storage.read(key: 'token');
      final url =
          '$server/download/scraper_output/$_scraperSerial/$serialOutput/';
      final response = await http.get(
        Uri.parse(url),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode != 200) {
        setState(() {
          _errorMessage = 'Download failed: ${response.body}';
        });
        return;
      }

      final bytes = response.bodyBytes;
      final blob = html.Blob([bytes], 'text/csv');
      final downloadUrl = html.Url.createObjectUrlFromBlob(blob);

      String filename = 'scraper_output_$serialOutput.csv';
      final contentDisposition = response.headers['content-disposition'] ?? '';
      final match = RegExp(
        r'filename="?([^"]+)"?',
      ).firstMatch(contentDisposition);
      if (match != null && match.groupCount > 0) {
        filename = match.group(1)!;
      }

      html.AnchorElement(href: downloadUrl)
        ..setAttribute('download', filename)
        ..click();
      html.Url.revokeObjectUrl(downloadUrl);
    } catch (e) {
      setState(() {
        _errorMessage = 'Error during download: $e';
      });
    }
  }

  Widget _buildTable() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('File Name')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Run Number')),
          DataColumn(label: Text('Created')),
          DataColumn(label: Text('Updated')),
          DataColumn(label: Text('Actions')),
        ],
        rows: _history.map((item) {
          return DataRow(
            cells: [
              DataCell(Text(item['file_name'] ?? '')),
              DataCell(Text(item['status'] ?? '')),
              DataCell(Text('${item['run_number'] ?? ''}')),
              DataCell(Text(item['create_date'] ?? '')),
              DataCell(Text(item['update_date'] ?? '')),
              DataCell(
                ElevatedButton(
                  onPressed: () => _downloadFile(item['serial_output']),
                  child: const Text('Download'),
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scraper History')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (_errorMessage != null)
                    Text(
                      _errorMessage!,
                      style: const TextStyle(color: Colors.red),
                    ),
                  if (_successMessage != null)
                    Text(
                      _successMessage!,
                      style: const TextStyle(color: Colors.green),
                    ),
                  const SizedBox(height: 16),
                  if (_history.isNotEmpty) Expanded(child: _buildTable()),
                ],
              ),
      ),
    );
  }
}
