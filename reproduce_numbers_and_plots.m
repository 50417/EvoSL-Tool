function reproduce_numbers_and_plots(evolSL36_db)
 disp("This can take a long time. .");
 x = analyzer(evolSL36_db);
 x.plot_and_print_results();
end