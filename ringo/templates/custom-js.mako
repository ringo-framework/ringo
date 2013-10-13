<!-- This snippet is included at the very end of the body after query has
been initialized. Overwrite this template to include custiom JS libraray and
code -->
<script src="http://d3js.org/d3.v3.js"></script>
% if h.get_app_name() == "ringo":
  <script src="/static/js/custom.js"></script>
% else:
  <script src="/${h.get_app_name()}-static/js/custom.js"></script>
%endif
