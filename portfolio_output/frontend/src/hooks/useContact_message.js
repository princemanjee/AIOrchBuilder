// File: hooks/useContact_message.js
import ('useState', 'useEffect') from 'react';
import supabase from '../lib/supabase';

export const useContact_message = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchContact_message = async () => {
            const { data, error } = await supabase.from('contact_messages').select('*');
            if (!error) setData(data);
            setLoading(false);
        };
        fetchContact_message();
    }, []);

    return { data, loading };
};
