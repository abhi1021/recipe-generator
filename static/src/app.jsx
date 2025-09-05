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

const Login = () => {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col justify-center items-center">
      <ThemeToggle />
      <div className="max-w-md w-full mx-auto p-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-8">Log in to your account</h2>
        <form action="/login" method="POST">
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</label>
            <input type="email" name="email" id="email" className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
            <input type="password" name="password" id="password" className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" />
          </div>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <input id="remember_me" name="remember_me" type="checkbox" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
              <label htmlFor="remember_me" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                Remember me
              </label>
            </div>
            <div className="text-sm">
              <a href="/forgot_password" className="font-medium text-primary-600 hover:text-primary-500">
                Forgot your password?
              </a>
            </div>
          </div>
          <div>
            <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              Log in
            </button>
          </div>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
          Don't have an account? <a href="/register" className="font-medium text-primary-600 hover:text-primary-500">Sign up</a>
        </p>
      </div>
    </div>
  );
};

const Register = () => {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col justify-center items-center">
      <ThemeToggle />
      <div className="max-w-md w-full mx-auto p-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-8">Create Account</h2>
        <form action="/register" method="POST">
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
            <input type="text" name="name" id="name" className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" />
          </div>
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</label>
            <input type="email" name="email" id="email" className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
            <input type="password" name="password" id="password" className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" />
          </div>
          <div className="mb-6">
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Confirm Password</label>
            <input type="password" name="confirm_password" id="confirm_password" className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm" />
          </div>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <input id="agree_terms" name="agree_terms" type="checkbox" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
              <label htmlFor="agree_terms" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                I agree to the <a href="#" className="text-primary-600 hover:text-primary-500">Terms of Service</a>
              </label>
            </div>
          </div>
          <div>
            <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              Register
            </button>
          </div>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
          Already have an account? <a href="/login" className="font-medium text-primary-600 hover:text-primary-500">Log in</a>
        </p>
      </div>
    </div>
  );
};

const Result = () => {
  const recipe = window.__RECIPE_DATA__;
  const shopping_list = window.__SHOPPING_LIST_DATA__;
  const have_items = window.__HAVE_ITEMS_DATA__;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <ThemeToggle />
      <nav className="bg-white dark:bg-gray-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex-shrink-0">
              <a href="/home" className="text-xl font-bold">Recipe Generator</a>
            </div>
            <div className="flex items-center">
              <a href="/logout" className="text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100">Logout</a>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
            <h2 className="text-3xl font-extrabold sm:text-4xl">
                {recipe.title}
            </h2>
            <p className="mt-4 text-lg text-gray-500 dark:text-gray-400">
                {recipe.description}
            </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
                <h3 className="text-2xl font-bold mb-4">Ingredients</h3>
                <ul className="list-disc list-inside space-y-2">
                    {recipe.ingredients.map((ing, i) => (
                        <li key={i}>{ing.quantity} {ing.unit} {ing.name}</li>
                    ))}
                </ul>

                <h3 className="text-2xl font-bold mt-8 mb-4">Instructions</h3>
                <ol className="list-decimal list-inside space-y-4">
                    {recipe.steps.map((step, i) => (
                        <li key={i}>{step}</li>
                    ))}
                </ol>
            </div>
            <div>
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                    <h3 className="text-xl font-bold mb-4">Shopping List</h3>
                    <ul className="space-y-2">
                        {shopping_list.map((item, i) => (
                            <li key={i} className="flex items-center">
                                <input type="checkbox" className="h-4 w-4 text-primary-600 border-gray-300 rounded" />
                                <span className="ml-2">{item.quantity} {item.unit} {item.name}</span>
                            </li>
                        ))}
                    </ul>
                    <h3 className="text-xl font-bold mt-6 mb-4">You Have</h3>
                    <ul className="space-y-2">
                        {have_items.map((item, i) => (
                            <li key={i} className="flex items-center text-gray-500 dark:text-gray-400 line-through">
                                <input type="checkbox" checked disabled className="h-4 w-4 text-primary-600 border-gray-300 rounded" />
                                <span className="ml-2">{item.quantity} {item.unit} {item.name}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
        <div className="mt-12 text-center">
            <a href="/home" className="text-primary-600 hover:text-primary-500">
                &larr; Back to Home
            </a>
        </div>
      </main>
    </div>
  );
};

const App = () => {
    const path = window.location.pathname;
    if (path === '/login') {
        return <Login />;
    }
    if (path === '/register') {
        return <Register />;
    }
    if (path.startsWith('/generate')) {
        // The result page is shown for any /generate path
        return <Result />;
    }
    return <Home />;
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
