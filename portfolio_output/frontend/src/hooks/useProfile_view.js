// File: hooks/useProfile_view.js
import ('useState', 'useEffect') from 'react';
import supabase from '../lib/supabase';

export const useProfile_view = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile_view = async () => {
            const { data, error } = await supabase.from('profile_views').select('*');
            if (!error) setData(data);
            setLoading(false);
        };
        fetchProfile_view();
    }, []);

    return { data, loading };
};
