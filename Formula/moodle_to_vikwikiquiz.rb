# frozen_string_literal: true

class MoodleToVikwikiquiz < Formula
  include Language::Python::Virtualenv

  desc "A CLI for converting a graded Moodle quiz HTML to a vik.wiki quiz wikitext."
  homepage "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz"
  url "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz/archive/v1.0.tar.gz"
  sha256 ""
  head "https://github.com/gy-mate/homebrew-moodle-to-vikwikiquiz.git"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/moodle-to-vikwikiquiz", "--version"
  end
end
