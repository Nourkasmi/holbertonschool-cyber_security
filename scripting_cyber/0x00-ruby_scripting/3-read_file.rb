#!/usr/bin/env ruby
require 'json'

def count_user_ids(path)
  data = JSON.parse(File.read(path))

  counts = Hash.new(0)

  data.each do |item|
    user_id = item["userId"]
    counts[user_id] += 1
  end

  counts.sort.each do |user_id, count|
    puts "#{user_id}: #{count}"
  end
end