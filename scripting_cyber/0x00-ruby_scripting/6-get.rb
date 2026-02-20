#!/usr/bin/env ruby
require 'net/http'
require 'json'
require 'uri'

def get_request(url)
  uri = URI.parse(url)
  response = Net::HTTP.get_response(uri)

  puts "Response status: #{response.code} #{response.message}"
  puts "Response body:"

  begin
    json_body = JSON.parse(response.body)
    puts JSON.pretty_generate(json_body)
  rescue JSON::ParserError
    puts response.body
  end
end