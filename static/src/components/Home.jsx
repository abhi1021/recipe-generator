const { useState, useEffect } = React;

const ThemeToggle = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
      setIsDarkMode(true);
    } else {
      document.documentElement.classList.remove('dark');
      setIsDarkMode(false);
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    setIsDarkMode(!isDarkMode);
  };

  return (
    <button onClick={toggleTheme} className="absolute top-4 right-4 p-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
      {isDarkMode ? 'Light' : 'Dark'}
    </button>
  );
};

const Home = () => {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <ThemeToggle />
      <nav className="bg-white dark:bg-gray-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold">Recipe Generator</h1>
            </div>
            <div className="flex items-center">
              <a href="/logout" className="text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100">Logout</a>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold sm:text-4xl">
            Create a new recipe
          </h2>
          <p className="mt-4 text-lg text-gray-500 dark:text-gray-400">
            Enter a prompt and some ingredients to generate a new recipe.
          </p>
        </div>
        <form action="/generate" method="POST" className="mt-12">
          <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-8">
            <div className="sm:col-span-2">
              <label htmlFor="recipe_prompt" className="block text-sm font-medium">Recipe Prompt</label>
              <div className="mt-1">
                <input type="text" name="recipe_prompt" id="recipe_prompt" className="py-3 px-4 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600" placeholder="e.g., a healthy chicken dish" />
              </div>
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="available_ingredients" className="block text-sm font-medium">Available Ingredients</label>
              <div className="mt-1">
                <textarea id="available_ingredients" name="available_ingredients" rows="4" className="py-3 px-4 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600" placeholder="e.g., chicken breast, rice, broccoli"></textarea>
              </div>
            </div>
            <div>
              <label htmlFor="servings" className="block text-sm font-medium">Servings</label>
              <div className="mt-1">
                <input type="text" name="servings" id="servings" className="py-3 px-4 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600" placeholder="e.g., 4" />
              </div>
            </div>
            <div>
              <label htmlFor="cuisine" className="block text-sm font-medium">Cuisine</label>
              <div className="mt-1">
                <input type="text" name="cuisine" id="cuisine" className="py-3 px-4 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600" placeholder="e.g., Italian" />
              </div>
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="time_pref" className="block text-sm font-medium">Time Preference</label>
              <div className="mt-1">
                <input type="text" name="time_pref" id="time_pref" className="py-3 px-4 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600" placeholder="e.g., 30 minutes" />
              </div>
            </div>
          </div>
          <div className="mt-8">
            <button type="submit" className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              Generate Recipe
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Home;
